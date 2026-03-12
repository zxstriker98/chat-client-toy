import json
import os
import time
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from pageindex import PageIndexClient
from tools.tools import tool

# ---------------------------------------------------------------------------
# Polling configuration
# ---------------------------------------------------------------------------
POLL_INTERVAL: float = 3.0   # seconds between status checks
MAX_POLL_TIME: float = 180.0
# ---------------------------------------------------------------------------
# Client singleton
# ---------------------------------------------------------------------------
_PI_CLIENT: PageIndexClient | None = None


def _get_client() -> PageIndexClient:
    global _PI_CLIENT
    if _PI_CLIENT is not None:
        return _PI_CLIENT

    api_key: str | None = os.getenv("PAGEINDEX_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PAGEINDEX_API_KEY env var. Set it to use page_index.")

    _PI_CLIENT = PageIndexClient(api_key=api_key)
    return _PI_CLIENT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _poll_tree_ready(client: PageIndexClient, doc_id: str) -> bool:
    """Poll until the document tree is ready or we time out."""
    deadline = time.monotonic() + MAX_POLL_TIME
    while time.monotonic() < deadline:
        if client.is_retrieval_ready(doc_id):
            return True
        time.sleep(POLL_INTERVAL)
    return False


def _poll_retrieval(client: PageIndexClient, retrieval_id: str) -> dict[str, Any]:
    """Poll ``get_retrieval`` until the result is ready or we time out."""
    deadline = time.monotonic() + MAX_POLL_TIME
    while time.monotonic() < deadline:
        data = client.get_retrieval(retrieval_id=retrieval_id)
        status = data.get("status", "").lower()
        if status in ("completed", "done", "ready"):
            return data
        if status in ("failed", "error"):
            return data
        time.sleep(POLL_INTERVAL)
    return {"status": "timeout", "message": f"Retrieval not ready after {MAX_POLL_TIME}s", "retrieval_id": retrieval_id}


def _format_tree_node(node: dict[str, Any], indent: int = 0) -> str:
    """Recursively format a tree node into a readable indented string."""
    prefix = "  " * indent
    title = node.get("title") or node.get("name") or "(untitled)"
    node_id = node.get("node_id", "")
    page = node.get("page_index", "")
    summary = node.get("summary", "")

    parts: list[str] = []
    header = f"{prefix}- {title}"
    if node_id:
        header += f"  [node_id={node_id}]"
    if page != "":
        header += f"  (page {page})"
    parts.append(header)

    if summary:
        parts.append(f"{prefix}  Summary: {summary}")

    for child in node.get("nodes", []):
        parts.append(_format_tree_node(child, indent + 1))

    return "\n".join(parts)


def _format_tree(data: dict[str, Any]) -> str:
    """Format the full tree response into a readable string."""
    tree = data.get("tree", data)

    if isinstance(tree, list):
        return "\n".join(_format_tree_node(node) for node in tree)

    if isinstance(tree, dict) and ("nodes" in tree or "title" in tree or "name" in tree):
        return _format_tree_node(tree)

    return json.dumps(data, indent=2, ensure_ascii=False)

class PageIndexParams(BaseModel):
    action: Literal[
        "submit", "get_tree", "query", "get_retrieval",
        "status", "list", "delete", "ocr",
    ] = Field(
        ...,
        description=(
            "Action to perform: "
            "'submit' — upload a document (polls until tree is ready); "
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

@tool(
    "page_index",
    "Index a document and query it using PageIndex vectorless RAG. "
    "Supports: submit (upload & wait), get_tree, query (ask & wait for answer), "
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
        client = _get_client()

        if action == "submit":
            data = client.submit_document(file_path=path)
            new_doc_id: str = data.get("doc_id", "")
            if not new_doc_id:
                return json.dumps({"action": "submit", "error": "No doc_id returned", "raw": data}, ensure_ascii=False)

            ready = _poll_tree_ready(client, new_doc_id)
            status_msg = "ready" if ready else f"still processing (poll again later with 'status' action)"
            return json.dumps({
                "action": "submit",
                "doc_id": new_doc_id,
                "status": status_msg,
                "hint": "Use 'query' action with this doc_id to ask questions, or 'get_tree' to see the document structure.",
            }, ensure_ascii=False)

        if action == "get_tree":
            data = client.get_tree(doc_id=doc_id, node_summary=True)
            status = data.get("status", "").lower()
            if status not in ("completed", "done", "ready", ""):
                ready = _poll_tree_ready(client, doc_id)
                if ready:
                    data = client.get_tree(doc_id=doc_id, node_summary=True)
                else:
                    return json.dumps({
                        "action": "get_tree",
                        "status": "processing",
                        "message": f"Tree not ready after {MAX_POLL_TIME}s. Try again later.",
                    }, ensure_ascii=False)

            formatted = _format_tree(data)
            return f"Document tree for {doc_id}:\n\n{formatted}"

        if action == "query":
            submit_data = client.submit_query(doc_id=doc_id, query=query)
            rid: str = submit_data.get("retrieval_id", "")
            if not rid:
                return json.dumps({"action": "query", "error": "No retrieval_id returned", "raw": submit_data}, ensure_ascii=False)

            result_data = _poll_retrieval(client, rid)
            return json.dumps({
                "action": "query",
                "query": query,
                "retrieval_id": rid,
                "result": result_data,
            }, indent=2, ensure_ascii=False)

        if action == "get_retrieval":
            data = client.get_retrieval(retrieval_id=retrieval_id)
            return json.dumps({"action": "get_retrieval", "result": data}, indent=2, ensure_ascii=False)

        if action == "status":
            data = client.get_document(doc_id=doc_id)
            retrieval_ready = client.is_retrieval_ready(doc_id)
            data["retrieval_ready"] = retrieval_ready
            return json.dumps({"action": "status", "result": data}, indent=2, ensure_ascii=False)

        if action == "list":
            data = client.list_documents()
            docs = data.get("documents", [])
            if not docs:
                return "No documents found."
            lines = [f"Found {data.get('total', len(docs))} document(s):\n"]
            for doc in docs:
                lines.append(
                    f"  - {doc.get('name', '?')}  [doc_id={doc.get('id', '?')}]  "
                    f"status={doc.get('status', '?')}  pages={doc.get('pageNum', '?')}"
                )
            return "\n".join(lines)

        if action == "delete":
            data = client.delete_document(doc_id=doc_id)
            return json.dumps({"action": "delete", "doc_id": doc_id, "result": data}, ensure_ascii=False)

        if action == "ocr":
            fmt = ocr_format or "raw"
            data = client.get_ocr(doc_id=doc_id, format=fmt)
            return json.dumps({"action": "ocr", "format": fmt, "result": data}, indent=2, ensure_ascii=False)

        return f"Error: Unknown action '{action}'"

    except RuntimeError as e:
        return str(e)
    except Exception as e:
        return f"Error ({type(e).__name__}): {e}"
