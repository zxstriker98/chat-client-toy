"""
PDFVisionExtractor — Extract structured data from PDF pages using GPT-4o Vision.

Use cases:
- Allergen tables (image-based grids)
- Price lists in graphic designs
- Any page where text extraction fails

Usage:
    extractor = PDFVisionExtractor()
    result = extractor.extract_page(pdf_path, page_num=1, prompt=ALLERGEN_PROMPT)
    print(result)  # Structured markdown table
"""

import base64
import os
from pathlib import Path

import pymupdf
from openai import OpenAI

# Constants for PDF processing and API calls
DEFAULT_PDF_ZOOM = 2.0
VISION_API_MAX_TOKENS = 4096

ALLERGEN_PROMPT = """This is a page from a restaurant menu PDF. It contains an allergen information table.

Please extract the COMPLETE allergen table and format it as a markdown table with:
- Rows = each dish/item
- Columns = each allergen type (Celery, Gluten, Crustaceans, Eggs, Fish, Lupin, Milk, Molluscs, Mustard, Nuts, Peanuts, Sesame, Soya, Sulphites)
- Use ✅ for contains allergen, ❌ for does not contain, ⚠️ for may contain

Also extract any dietary labels visible:
- (v) = vegetarian
- (vg) = vegan  
- (GF) = gluten free

Return ONLY the markdown table and dietary notes. No other text."""


class PDFVisionExtractor:
    """Extract structured data from PDF pages using GPT-4o Vision API."""

    def __init__(self, model: str = "gpt-4o", zoom: float = DEFAULT_PDF_ZOOM):
        """
        Args:
            model: Vision-capable model to use (default: gpt-4o)
            zoom: Page render zoom factor for clarity (default: 2x)
        """
        self.model = model
        self.zoom = zoom
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _render_page_as_base64(self, pdf_path: str, page_num: int) -> str:
        """Render a PDF page as a base64-encoded PNG image."""
        try:
            doc = pymupdf.open(pdf_path)
        except Exception as e:
            raise ValueError(f"Failed to open PDF: {e}")
            
        if page_num >= len(doc):
            raise ValueError(f"Page {page_num} does not exist (PDF has {len(doc)} pages)")

        page = doc[page_num]
        mat = pymupdf.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        return base64.b64encode(img_bytes).decode("utf-8")

    def extract_page(self, pdf_path: str, page_num: int = 0, prompt: str = None) -> str:
        """
        Extract structured data from a PDF page using Vision API.

        Args:
            pdf_path: Path to PDF file
            page_num: Zero-based page number to extract (default: 0)
            prompt: Custom extraction prompt. Defaults to ALLERGEN_PROMPT.

        Returns:
            Extracted text/table as string
        """
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        prompt = prompt or ALLERGEN_PROMPT
        print(f"  Rendering page {page_num + 1} of {Path(pdf_path).name}...")
        img_b64 = self._render_page_as_base64(pdf_path, page_num)
        print(f"  Sending to {self.model} Vision API...")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_b64}",
                                "detail": "high"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            max_tokens=VISION_API_MAX_TOKENS
        )

        return response.choices[0].message.content

    def extract_all_pages(self, pdf_path: str, prompt: str = None) -> list[str]:
        """Extract structured data from all pages of a PDF."""
        doc = pymupdf.open(pdf_path)
        results = []
        for page_num in range(len(doc)):
            print(f"\n--- Page {page_num + 1}/{len(doc)} ---")
            result = self.extract_page(pdf_path, page_num, prompt)
            results.append(result)
        return results
