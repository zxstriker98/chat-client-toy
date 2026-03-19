"""
PageIndexService — encapsulates all PageIndex local processing logic.

Handles document processing, tree generation, and chunk management
using the local PageIndex library instead of a hosted API.
"""

import json
import os
from typing import Any
from pageindex_lib.page_index import config, page_index_main


class PageIndexService:
    """High-level wrapper around the local PageIndex library."""

    def __init__(self, model: str = "gpt-4o-2024-11-20"):
        """
        Initialize PageIndexService with local PageIndex library.
        
        Args:
            model: LLM model to use for tree generation (default: gpt-4o-2024-11-20)
        """
        self.model = model
        self.config_opts = config(
            model=model,
            toc_check_page_num=20,
            max_page_num_each_node=10,
            max_token_num_each_node=20000,
            if_add_node_id="yes",
            if_add_node_summary="yes",
            if_add_doc_description="no",
            if_add_node_text="no"
        )

    def process_document(self, file_path: str) -> dict:
        """
        Process a document locally to generate tree structure.
        
        Args:
            file_path: Path to the PDF file.
            
        Returns:
            The tree structure dict with format: {"doc_name": "...", "structure": [...]}
            
        Raises:
            FileNotFoundError: If file doesn't exist.
            RuntimeError: If processing fails.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"Only PDF files supported: {file_path}")
        
        try:
            tree = page_index_main(file_path, self.config_opts)
            return tree
        except Exception as e:
            raise RuntimeError(f"Failed to process document: {e}")

    def get_tree(self, file_path: str, node_summary: bool = True) -> dict[str, Any]:
        """
        Fetch the document tree.
        
        Args:
            file_path: Path to the PDF file.
            node_summary: Include AI-generated summaries per node.
            
        Returns:
            The tree structure dict.
        """
        return self.process_document(file_path)

    def get_formatted_tree(self, file_path: str) -> str:
        """Fetch the tree and return a human-readable formatted string."""
        data = self.get_tree(file_path)
        return self.format_tree(data)

    @staticmethod
    def format_tree(data: dict[str, Any]) -> str:
        """Format a tree response into a readable indented string."""
        tree = data.get("structure", data.get("tree", data))

        if isinstance(tree, list):
            return "\n".join(
                PageIndexService._format_node(node) for node in tree
            )

        if isinstance(tree, dict) and (
            "nodes" in tree or "title" in tree or "name" in tree
        ):
            return PageIndexService._format_node(tree)

        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def _format_node(node: dict[str, Any], indent: int = 0) -> str:
        """Recursively format a single tree node."""
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
            parts.append(PageIndexService._format_node(child, indent + 1))

        return "\n".join(parts)
