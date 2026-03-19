import json
from typing import Any

from providers.ProviderFactory import ProviderFactory
from providers.base import AsyncBaseLLMClient

from database.connection import create_db
from database.ChunkRecord import ChunkRecord
from database.repository.ChunkRepository import ChunkRepository
from database.repository.FileRepository import FileRepository


RANKING_SYSTEM_PROMPT = """You are a document chunk relevance ranker.

Given a user query and a list of document chunks (each with an ID, title, path, and summary),
return the IDs of the most relevant chunks ranked by relevance to the query.

Respond with ONLY a JSON array of chunk IDs, most relevant first. Example: [5, 12, 3]

Rules:
- Return only chunks that are actually relevant to the query
- Return at most {top_k} chunk IDs
- If no chunks are relevant, return an empty array: []
- Do NOT include any explanation, just the JSON array"""


class ChunkContext:
    """Searches stored chunks using LLM-based ranking and formats them as context."""

    def __init__(
        self,
        db_path: str = "data/pageindex_cache.db",
        model: str = "gpt-4.1-mini",
        default_top_k: int = 5,
    ):
        session_factory = create_db(db_path)
        self._session = session_factory()
        self._repo = ChunkRepository(self._session)
        self._file_repo = FileRepository(self._session)

        self._model = model

        self._default_top_k = default_top_k
        self._client_top_k = default_top_k

        self._client: AsyncBaseLLMClient = ProviderFactory.from_model(
            model_name=self._model,
            instructions=RANKING_SYSTEM_PROMPT.format(top_k=default_top_k),
        )

        self._chunks: list[ChunkRecord] = []
        self._chunk_map: dict[int, ChunkRecord] = {}
        self._filehash_to_doc: dict[str, str] = {}
        self._filehash_to_name: dict[str, str] = {}

    def load_chunks(self, file_hashes: list[str] | None = None) -> int:
        """Load chunks from the DB into memory.

        Args:
            file_hashes: Optional filter — only load chunks for these files.

        Returns:
            Number of chunks loaded.
        """
        if file_hashes:
            self._chunks = []
            for fh in file_hashes:
                self._chunks.extend(self._repo.get_by_file(fh))
        else:
            self._chunks = self._repo.get_all() if hasattr(self._repo, "get_all") else (
                self._session.query(ChunkRecord).all()
            )

        self._chunk_map = {c.chunk_id: c for c in self._chunks}

        # Cache file_hash -> doc_id and file_name for routing
        files = self._file_repo.get_all()
        self._filehash_to_doc = {f.file_hash: f.doc_id for f in files}
        self._filehash_to_name = {f.file_hash: f.file_name for f in files}
        return len(self._chunks)

    def _build_chunk_catalog(self) -> str:
        """Build a compact catalog of all chunks for the LLM to evaluate."""
        lines: list[str] = []
        for c in self._chunks:
            path = c.node_path or c.node_title or ""
            summary = c.node_summary or ""
            entry = f"[{c.chunk_id}] {path}"
            if summary:
                entry += f" — {summary}"
            lines.append(entry)
        return "\n".join(lines)

    def _parse_chunk_id_list(self, raw: str, top_k: int) -> list[int]:
        """Parse/validate the model response as a JSON array of chunk IDs (list[int])."""
        s = raw.strip()

        if s.startswith("```"):
            s = s.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        data = json.loads(s)
        if not isinstance(data, list):
            raise ValueError("Expected JSON array of chunk IDs")

        out: list[int] = []
        for x in data:
            if isinstance(x, int):
                out.append(x)
            elif isinstance(x, str) and x.isdigit():
                out.append(int(x))

        seen: set[int] = set()
        deduped: list[int] = []
        for cid in out:
            if cid not in seen:
                seen.add(cid)
                deduped.append(cid)

        return deduped[:top_k]

    def _ensure_client_for_top_k(self, top_k: int) -> None:
        """Ensure the provider client has instructions compiled for this top_k."""
        if top_k == self._client_top_k:
            return
        self._client = ProviderFactory.from_model(
            model_name=self._model,
            instructions=RANKING_SYSTEM_PROMPT.format(top_k=top_k),
        )
        self._client_top_k = top_k

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Search chunks using LLM-based relevance ranking.

        Sends all chunk titles/summaries to the LLM in a single call
        and asks it to pick the most relevant chunk IDs.

        Args:
            query: The user's query.
            top_k: Maximum number of results to return.

        Returns:
            List of result dicts sorted by LLM-determined relevance.
        """
        if not self._chunks:
            return []

        self._ensure_client_for_top_k(top_k)

        catalog = self._build_chunk_catalog()

        # With instructions set on the client, the query only needs user/task payload.
        prompt = f"""User query: {query}

Available chunks:
{catalog}

Return the IDs of the {top_k} most relevant chunks as a JSON array."""

        try:
            raw = (await self._client.generate_response(prompt)).strip()
            chunk_ids = self._parse_chunk_id_list(raw, top_k)

        except Exception as e:
            print(f"  [LLM ranking failed: {e}, falling back to first {top_k}]")
            chunk_ids = [c.chunk_id for c in self._chunks[:top_k]]

        results: list[dict[str, Any]] = []
        for rank, cid in enumerate(chunk_ids):
            chunk = self._chunk_map.get(cid)
            if not chunk:
                continue
            results.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "file_hash": chunk.file_hash,
                    "node_title": chunk.node_title or "",
                    "node_path": chunk.node_path or chunk.node_title or "",
                    "node_summary": chunk.node_summary or "",
                    "page_index": chunk.page_index,
                    "text": chunk.text,
                    "rank": rank + 1,
                }
            )

        return results


    async def route_doc_ids(self, query: str, chunk_top_k: int = 8, doc_top_n: int = 2) -> list[dict[str, Any]]:
        """Route a query to the most relevant PageIndex doc_id(s) using chunk ranking.

        Strategy:
          1) Rank top chunk_top_k chunks via existing LLM ranker.
          2) Aggregate by file_hash.
          3) Return top doc_top_n documents by count.

        Returns:
            List of dicts: {doc_id, file_name, file_hash, score}
        """
        if not self._chunks:
            return []

        ranked_chunks = await self.search(query, top_k=chunk_top_k)
        if not ranked_chunks:
            return []

        counts: dict[str, int] = {}
        for r in ranked_chunks:
            fh = r.get("file_hash")
            if not fh:
                continue
            counts[fh] = counts.get(fh, 0) + 1

        ranked_files = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:doc_top_n]

        out: list[dict[str, Any]] = []
        for fh, score in ranked_files:
            doc_id = self._filehash_to_doc.get(fh)
            if not doc_id:
                continue
            out.append(
                {
                    "doc_id": doc_id,
                    "file_name": self._filehash_to_name.get(fh, ""),
                    "file_hash": fh,
                    "score": score,
                }
            )
        return out

    def format_context(self, results: list[dict[str, Any]]) -> str:
        """Format search results as context text for the LLM.

        Each chunk is formatted as: path → summary → text

        Args:
            results: Search results from self.search().

        Returns:
            Formatted context string, or empty string if no results.
        """
        if not results:
            return ""

        parts = ["[Relevant document context]"]
        for r in results:
            path = r.get("node_path") or r.get("node_title", "")
            summary = r.get("node_summary", "")
            page = r["page_index"]

            header = f"--- [{path}]"
            if page is not None:
                header += f" (page {page})"
            header += " ---"
            parts.append(header)

            if summary:
                parts.append(f"Summary: {summary}")
                parts.append("")

            parts.append(r["text"])
        parts.append("[End of context]")
        return "\n".join(parts)

    async def enrich(self, query: str, top_k: int = 5) -> str:
        """Search chunks and build an enriched query with context.

        Args:
            query: The original user query.
            top_k: Number of chunks to include.

        Returns:
            The enriched query with context prepended, or the original
            query if no relevant chunks were found.
        """
        results = await self.search(query, top_k=top_k)
        context = self.format_context(results)
        if not context:
            return query
        return f"{context}\n\n{query}"

    @property
    def chunk_count(self) -> int:
        """Number of chunks loaded."""
        return len(self._chunks)

    def close(self):
        """Close the database session."""
        self._session.close()