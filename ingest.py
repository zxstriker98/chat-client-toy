"""
Document ingestion using local PageIndex processing.

This script processes PDFs using the PageIndex library to build tree structures
and populates the local database for RAG.

Usage:
    python ingest.py data/alpha_handbook.pdf
    python ingest.py data/*.pdf --model gpt-4o
"""

import json
import hashlib
from pathlib import Path

import pymupdf
from dotenv import load_dotenv

from database.connection import create_db
from database.FileRecord import FileRecord
from database.ChunkRecord import ChunkRecord
from database.repository.FileRepository import FileRepository
from database.repository.ChunkRepository import ChunkRepository
from services.PageIndexService import PageIndexService


def file_hash(path: str) -> str:
    """Compute MD5 hash of a file."""
    h = hashlib.md5()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def process_pdf_local(pdf_path: str, service: PageIndexService, summary_prompt: str = None) -> dict:
    """
    Process a PDF using PageIndex library.
    Returns the tree structure.
    """
    print(f"  Processing {Path(pdf_path).name}...")
    
    try:
        # Temporarily attach custom prompt to service config if provided
        if summary_prompt:
            service.config_opts.summary_prompt_template = summary_prompt
        elif hasattr(service.config_opts, 'summary_prompt_template'):
            del service.config_opts.summary_prompt_template
        tree = service.process_document(pdf_path)
        print(f"  Tree generated successfully")
        return tree
    except Exception as e:
        print(f"  Failed to process PDF: {e}")
        raise


def flatten_tree(nodes: list, ancestors: list = None, file_hash_val: str = "") -> list:
    """
    Flatten tree structure into chunks.
    Each node becomes a chunk with its path/context.
    """
    if ancestors is None:
        ancestors = []
    
    chunks = []
    
    for node in nodes:
        if not isinstance(node, dict):
            continue
        
        title = node.get("title", node.get("name", "(untitled)"))
        node_id = node.get("node_id", "")
        page = node.get("page_index", "")
        summary = node.get("summary", "")
        raw_text = node.get("text", "")  # Raw page text (includes prices!)
        
        # Build breadcrumb path
        path_parts = ancestors + [title]
        path = " > ".join(path_parts)

        # Prefer raw text (has prices/details) → fallback to summary → fallback to title
        chunk_text = raw_text or summary or title
        
        # Create chunk record
        chunk = ChunkRecord(
            file_hash=file_hash_val,
            node_id=node_id or f"node_{len(chunks)}",
            node_path=path,
            node_title=title,
            page_index=page if page != "" else None,
            node_summary=summary or "",
            text=chunk_text,
            chunk_index=len(chunks),
        )
        chunks.append(chunk)
        
        # Process children recursively
        children = node.get("nodes", [])
        if children:
            child_chunks = flatten_tree(
                children,
                ancestors=path_parts,
                file_hash_val=file_hash_val
            )
            chunks.extend(child_chunks)
    
    return chunks


VISION_EXTRACTION_PROMPT = """Describe EVERYTHING you see on this page in complete detail. Include:
- All dish names exactly as written
- All prices (numbers near dish names are prices in £)
- All dietary markers: (v)=vegetarian, (vg)=vegan, (gf)=gluten free
- All descriptions word for word
- Any allergen symbols or tables
- Any section headings

Format each dish as: "DISH NAME (dietary) — £price: description"
Be exhaustive and precise. Do not summarise or omit anything."""


MENU_SUMMARY_PROMPT = """You are given raw text extracted from a restaurant menu PDF. Your task is to produce a structured summary that preserves ALL factual details.

CRITICAL RULES:
- ALWAYS preserve prices exactly as they appear (numbers next to dish names are prices in £)
- ALWAYS preserve dish names and product names exactly
- ALWAYS preserve allergen and dietary info (v=vegetarian, vg=vegan, GF=gluten free)
- Format each menu item as: "DISH NAME — £price: description (dietary info)"
- Numbers appearing after or near a dish name are prices (e.g. "GOL GAPPA | ... | 5" means £5)
- If a price is genuinely not visible, write "price not listed"
- Do NOT generalise — be specific and factual

Raw Menu Text: {text}

Return a structured factual summary with all dish names, prices and descriptions. Do not include any other text.
"""


def ingest_pdf_vision(
    pdf_path: str,
    file_repo: FileRepository,
    chunk_repo: ChunkRepository,
    reingest: bool = False,
    prompt: str = None,
    vision_model: str = "gpt-4o",
) -> int:
    """
    Ingest a PDF using GPT-4o Vision API — renders each page as image and extracts
    structured text. Best for menus/PDFs where text is image-based (prices in graphics,
    allergen tables, etc).

    Returns:
        Number of chunks created.
    """
    from services.PDFVisionExtractor import PDFVisionExtractor

    path = Path(pdf_path)
    if not path.exists():
        print(f"  File not found: {pdf_path}")
        return 0

    fhash = file_hash(pdf_path)
    existing = file_repo.get_by_hash(fhash)

    if existing and not reingest:
        existing_chunks = chunk_repo.count(file_hash=fhash)
        print(f"  Already ingested: {path.name} ({existing_chunks} chunks)")
        return 0

    if existing and reingest:
        deleted = chunk_repo.delete_by_file(fhash)
        print(f"  Cleared {deleted} old chunks")

    print(f"[{path.name}] — Vision mode")

    extractor = PDFVisionExtractor(model=vision_model)
    doc = pymupdf.open(pdf_path)
    num_pages = len(doc)
    extraction_prompt = prompt or VISION_EXTRACTION_PROMPT

    chunks = []
    for page_num in range(num_pages):
        print(f"  Extracting page {page_num + 1}/{num_pages}...")
        try:
            text = extractor.extract_page(pdf_path, page_num, prompt=extraction_prompt)
        except Exception as e:
            print(f"  Vision extraction failed for page {page_num + 1}: {e}")
            continue

        chunk = ChunkRecord(
            file_hash=fhash,
            node_id=f"vision_page_{page_num + 1}",
            node_path=f"{path.stem} > Page {page_num + 1}",
            node_title=f"Page {page_num + 1}",
            page_index=page_num + 1,
            node_summary=text,
            text=text,
            chunk_index=page_num,
        )
        chunks.append(chunk)

    if not chunks:
        print("  No chunks generated")
        return 0

    # Save file record
    file_record = FileRecord(
        file_hash=fhash,
        file_name=path.name,
        doc_id=f"vision_{fhash[:8]}",
        file_format="pdf_vision",
        file_size=path.stat().st_size,
    )
    file_repo.insert(file_record)

    for chunk in chunks:
        chunk_repo.insert(chunk)

    print(f"  Vision-ingested {len(chunks)} page chunks")
    return len(chunks)


def ingest_pdf(
    pdf_path: str,
    file_repo: FileRepository,
    chunk_repo: ChunkRepository,
    service: PageIndexService,
    reingest: bool = False,
    summary_prompt: str = None,
) -> int:
    """
    Ingest a PDF using PageIndex processing.
    
    Returns:
        Number of chunks created.
    """
    path = Path(pdf_path)
    
    if not path.exists():
        print(f"  File not found: {pdf_path}")
        return 0
    
    if path.suffix.lower() != ".pdf":
        print(f"  Skipping non-PDF: {pdf_path}")
        return 0
    
    fhash = file_hash(pdf_path)
    existing = file_repo.get_by_hash(fhash)
    
    # Check if already ingested
    if existing and not reingest:
        existing_chunks = chunk_repo.count(file_hash=fhash)
        print(f"  Already ingested: {path.name} ({existing_chunks} chunks)")
        return 0
    
    if existing and reingest:
        deleted = chunk_repo.delete_by_file(fhash)
        print(f"  Cleared {deleted} old chunks")
    
    print(f"[{path.name}]")
    
    # Process PDF
    try:
        tree = process_pdf_local(pdf_path, service, summary_prompt=summary_prompt)
    except Exception as e:
        print(f"  Processing failed: {e}")
        return 0
    
    # Extract nodes from tree response
    # PageIndex returns: {"doc_name": "...", "structure": [...]}
    if isinstance(tree, dict):
        nodes = tree.get("structure", tree.get("result", []))
    elif isinstance(tree, list):
        nodes = tree
    else:
        nodes = []
    
    if not nodes:
        print(f"  No tree nodes found")
        return 0
    
    # Flatten tree into chunks
    chunks = flatten_tree(nodes, file_hash_val=fhash)
    if not chunks:
        print(f"  No chunks generated")
        return 0
    
    # Create file record
    file_record = FileRecord(
        file_hash=fhash,
        file_name=path.name,
        doc_id=f"local_{fhash[:8]}",
        file_format="pdf",
        file_size=path.stat().st_size,
    )
    file_repo.insert(file_record)
    
    # Insert chunks
    for chunk in chunks:
        chunk_repo.insert(chunk)
    
    print(f"  Ingested {len(chunks)} chunks")
    return len(chunks)


def main():
    load_dotenv()
    
    import argparse
    parser = argparse.ArgumentParser(description="Ingest PDFs using PageIndex processing")
    parser.add_argument("files", nargs="*", help="PDF files to ingest")
    parser.add_argument("--db", default="data/pageindex_cache.db", help="Database path")
    parser.add_argument("--model", default="gpt-4o-2024-11-20", help="LLM model to use")
    parser.add_argument("--reingest", action="store_true", help="Re-ingest even if already processed")
    parser.add_argument("--clear", action="store_true", help="Clear database")
    parser.add_argument("--list", action="store_true", help="List ingested documents")
    parser.add_argument("--menu", action="store_true", help="Use menu-optimised prompt that preserves prices and dish names (only applies with --no-vision)")
    parser.add_argument("--no-vision", action="store_true", help="Use PageIndex text extraction instead of GPT-4o Vision (faster but less accurate for graphic PDFs)")
    parser.add_argument("--vision-model", type=str, default="gpt-4o", help="Vision model to use for PDF extraction (default: gpt-4o). Options: gpt-4o, gpt-4o-mini, gpt-4-turbo")
    
    args = parser.parse_args()
    
    # Create database
    SessionMaker = create_db(args.db)
    session = SessionMaker()
    file_repo = FileRepository(session)
    chunk_repo = ChunkRepository(session)
    
    try:
        # Handle --clear
        if args.clear:
            chunk_count = chunk_repo.count()
            chunk_repo.delete_all()
            
            # Also clear file records
            from database.FileRecord import FileRecord
            file_count = session.query(FileRecord).delete()
            session.commit()
            
            print(f"Cleared {chunk_count} chunks and {file_count} files from database")
            return
        
        # Handle --list
        if args.list:
            files = file_repo.get_all()
            if not files:
                print("No documents ingested yet.")
                return
            print(f"{len(files)} documents in database:")
            for f in files:
                chunk_count = chunk_repo.count(file_hash=f.file_hash)
                print(f"  - {f.file_name} ({chunk_count} chunks)")
            return
        
        # Handle file ingestion
        if not args.files:
            parser.print_help()
            return
        
        # Create PageIndex service
        service = PageIndexService(model=args.model)
        
        total = 0
        for pdf in args.files:
            if not args.no_vision:
                # DEFAULT: Vision mode — render pages as images, extract with GPT-4o Vision
                # Most accurate for graphic PDFs, menus, allergen tables
                print(f"  Using Vision API [{args.vision_model}] for: {Path(pdf).name}")
                count = ingest_pdf_vision(
                    pdf,
                    file_repo,
                    chunk_repo,
                    reingest=args.reingest,
                    vision_model=args.vision_model,
                )
            else:
                # FALLBACK: PageIndex text extraction (--no-vision flag)
                # Faster but less accurate for graphic/designed PDFs
                is_menu = args.menu or any(
                    kw in Path(pdf).name.lower()
                    for kw in ["menu", "food", "drink", "price"]
                )
                summary_prompt = MENU_SUMMARY_PROMPT if is_menu else None
                if is_menu:
                    print(f"  Using menu-optimised prompt (text mode) for: {Path(pdf).name}")
                else:
                    print(f"  Using PageIndex text extraction for: {Path(pdf).name}")

                count = ingest_pdf(
                    pdf,
                    file_repo,
                    chunk_repo,
                    service,
                    reingest=args.reingest,
                    summary_prompt=summary_prompt,
                )
            total += count
        
        print(f"\nDone - {total} total chunks ingested from {len(args.files)} file(s)")
        print(f"Database: {args.db}")
    
    finally:
        session.close()


if __name__ == "__main__":
    main()
