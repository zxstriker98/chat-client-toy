import json
import os
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from pageindex import PageIndexClient
from services.PageIndexService import PageIndexService
from database.cache import PageIndexCacheService
from database.connection import create_db
from database.repository.FileRepository import FileRepository
from tools.tools import tool

# ---------------------------------------------------------------------------
# Singletons — lazily initialized
# ---------------------------------------------------------------------------
_SERVICE: PageIndexService | None = None
_CACHE: PageIndexCacheService | None = None


def _get_service() -> PageIndexService:
    global _SERVICE
    if _SERVICE is not None:
        return _SERVICE

    api_key: str | None = os.getenv("PAGEINDEX_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PAGEINDEX_API_KEY env var. Set it to use page_index.")

    client = PageIndexClient(api_key=api_key)
    _SERVICE = PageIndexService(client)
    return _SERVICE

def _get_cache() -> PageIndexCacheService:
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    db_path = os.getenv("PAGEINDEX_DB_PATH", "data/pageindex_cache.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    session_factory = create_db(db_path)
    repo = FileRepository(session_factory())
    _CACHE = PageIndexCacheService(repo)
    return _CACHE


# ---------------------------------------------------------------------------
# Param model
# ---------------------------------------------------------------------------

class PageIndexParams(BaseModel):
    action: Literal[
        "submit", "get_tree", "query", "get_retrieval",
        "status", "list", "delete", "ocr",
    ] = Field(
        ...,
        description=(
            "Action to perform: "
            "'submit' — upload a document (uses cache to skip re-uploads); "
            "'get_tree' — get the document's hierarchical tree; "
            "'query' — ask a question against a document (polls until answer is ready); "
            "'get_retrieval' — fetch a previous retrieval result; "
            "'status' — check document processing status; "
            "'list' — list all indexed documents; "
            "'delete' — delete a document; "
            "'ocr' — get OCR text for a document."
        ),
    )
    query: str | None = Field(default=None, description="Question to ask (required for 'query')")
    doc_id: str | None = Field(default=None, description="Document ID (required for get_tree, query, status, delete, ocr)")
    path: str | None = Field(default=None, description="File path to upload (required for 'submit')")
    retrieval_id: str | None = Field(default=None, description="Retrieval ID (required for 'get_retrieval')")
    ocr_format: str | None = Field(default="raw", description="OCR format: 'page', 'node', or 'raw' (default 'raw')")

    @model_validator(mode="after")
    def check_required_fields(self):
        if self.action == "submit" and self.path is None:
            raise ValueError("'path' is required when action is 'submit'")
        if self.action in ("get_tree", "status", "delete", "ocr") and self.doc_id is None:
            raise ValueError(f"'doc_id' is required when action is '{self.action}'")
        if self.action == "query":
            if self.doc_id is None:
                raise ValueError("'doc_id' is required when action is 'query'")
            if self.query is None:
                raise ValueError("'query' is required when action is 'query'")
        if self.action == "get_retrieval" and self.retrieval_id is None:
            raise ValueError("'retrieval_id' is required when action is 'get_retrieval'")
        return self


# ---------------------------------------------------------------------------
# Tool implementation
# ---------------------------------------------------------------------------

@tool(
    "page_index",
    "Index a document and query it using PageIndex vectorless RAG. "
    "Supports: submit (upload & wait, cached), get_tree, query (ask & wait for answer), "
    "get_retrieval, status, list, delete, ocr.",
    PageIndexParams,
)
def page_index(
    action: str,
    path: str | None = None,
    doc_id: str | None = None,
    query: str | None = None,
    retrieval_id: str | None = None,
    ocr_format: str | None = "raw",
) -> str:
    """Submit, inspect, or query documents via the PageIndex API."""
    try:
        service = _get_service()

        # ---- submit (with cache) -------------------------------------------
        if action == "submit":
            cache = _get_cache()
            doc_id = cache.get_or_submit(service, path)
            return json.dumps({
                "action": "submit",
                "doc_id": doc_id,
                "status": "ready",
                "hint": "Use 'query' action with this doc_id to ask questions, or 'get_tree' to see the document structure.",
            }, ensure_ascii=False)

        # ---- get_tree ------------------------------------------------------
        if action == "get_tree":
            formatted = service.get_formatted_tree(doc_id)
            return f"Document tree for {doc_id}:\n\n{formatted}"

        # ---- query ---------------------------------------------------------
        if action == "query":
            result_data = service.query_and_wait(doc_id, query)
            return json.dumps({
                "action": "query",
                "query": query,
                "result": result_data,
            }, indent=2, ensure_ascii=False)

        # ---- get_retrieval -------------------------------------------------
        if action == "get_retrieval":
            data = service.get_retrieval(retrieval_id)
            return json.dumps({"action": "get_retrieval", "result": data}, indent=2, ensure_ascii=False)

        # ---- status --------------------------------------------------------
        if action == "status":
            data = service.get_status(doc_id)
            return json.dumps({"action": "status", "result": data}, indent=2, ensure_ascii=False)

        # ---- list ----------------------------------------------------------
        if action == "list":
            docs = service.list_documents()
            if not docs:
                return "No documents found."
            lines = [f"Found {len(docs)} document(s):\n"]
            for doc in docs:
                lines.append(
                    f"  - {doc.get('name', '?')}  [doc_id={doc.get('id', '?')}]  "
                    f"status={doc.get('status', '?')}  pages={doc.get('pageNum', '?')}"
                )
            return "\n".join(lines)

        # ---- delete --------------------------------------------------------
        if action == "delete":
            data = service.delete_document(doc_id)
            return json.dumps({"action": "delete", "doc_id": doc_id, "result": data}, ensure_ascii=False)

        # ---- ocr -----------------------------------------------------------
        if action == "ocr":
            fmt = ocr_format or "raw"
            data = service.get_ocr(doc_id, fmt)
            return json.dumps({"action": "ocr", "format": fmt, "result": data}, indent=2, ensure_ascii=False)

        return f"Error: Unknown action '{action}'"

    except RuntimeError as e:
        return str(e)
    except TimeoutError as e:
        return f"Timeout: {e}"
    except Exception as e:
        return f"Error ({type(e).__name__}): {e}"
