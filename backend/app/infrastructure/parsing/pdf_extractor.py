"""
PDF text and structure extraction via pdfplumber.

Honest limitations (documented here rather than hidden): PDF is a
rendering format, not a semantic one, so some ATS-risk signals can
only be approximated:

- `uses_text_boxes`: true vector text-box detection would require
  walking pdfplumber's low-level object graph for overlapping/rotated
  text runs. We approximate using annotation objects (FreeText
  annotations), which catches some but not all cases. This is flagged
  as a known gap, not silently assumed accurate.
- `has_images_with_text`: we cannot OCR here (that's a deliberate
  scope boundary -- OCR belongs in a dedicated pipeline, not resume
  parsing). We approximate by flagging large images (>40% of page
  area), since "resume as a single embedded image" is the common
  ATS-breaking pattern this check exists to catch.
"""

from __future__ import annotations

import io

import pdfplumber

from app.domain.entities.resume import FormattingFlags
from app.infrastructure.parsing.raw_document import RawDocument

_STANDARD_FONT_KEYWORDS = (
    "arial", "helvetica", "times", "calibri", "cambria", "georgia",
    "verdana", "garamond", "tahoma", "trebuchet", "segoe",
)
_LARGE_IMAGE_AREA_RATIO = 0.40


def extract_pdf(file_bytes: bytes) -> RawDocument:
    text_parts: list[str] = []
    uses_tables = False
    has_large_image = False
    non_standard_fonts = False
    uses_text_boxes = False

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        page_count = len(pdf.pages)

        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)

            if page.find_tables():
                uses_tables = True

            page_area = page.width * page.height
            for image in page.images:
                image_area = (image.get("width", 0)) * (image.get("height", 0))
                if page_area > 0 and (image_area / page_area) > _LARGE_IMAGE_AREA_RATIO:
                    has_large_image = True

            fonts_on_page = {
                char.get("fontname", "").lower() for char in page.chars
            }
            for font in fonts_on_page:
                if font and not any(kw in font for kw in _STANDARD_FONT_KEYWORDS):
                    non_standard_fonts = True

            annotations = page.annots or []
            if any(
                (annot.get("data", {}) or {}).get("Subtype") == "FreeText"
                for annot in annotations
            ):
                uses_text_boxes = True

    flags = FormattingFlags(
        uses_tables=uses_tables,
        uses_text_boxes=uses_text_boxes,
        uses_columns=False,  # column-layout detection deferred; see README
        non_standard_fonts=non_standard_fonts,
        has_images_with_text=has_large_image,
        page_count=page_count,
    )
    return RawDocument(text="\n".join(text_parts), formatting_flags=flags)
