"""
Image extractor for PNG, JPG, and JPEG resume uploads using Pillow and pytesseract OCR.
"""

import io
from PIL import Image
from app.domain.entities.resume import FormattingFlags
from app.infrastructure.parsing.raw_document import RawDocument


def extract_image(file_bytes: bytes) -> RawDocument:
    text = ""
    try:
        image = Image.open(io.BytesIO(file_bytes))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        import pytesseract
        text = pytesseract.image_to_string(image)
    except Exception as e:
        # Check if basic image loading worked but pytesseract is missing/failed
        raise ValueError(
            "Could not perform OCR text extraction on this image. "
            "Please ensure you upload a clear, text-readable PDF or DOCX file, or a high-contrast image."
        ) from e

    if not text or len(text.strip()) < 10:
        raise ValueError(
            "Unable to read text from this image file. The image may be blurry, low resolution, or empty. "
            "Please upload a clear, high-resolution document."
        )

    flags = FormattingFlags(
        uses_tables=False,
        uses_text_boxes=False,
        non_standard_fonts=False,
        has_images_with_text=True,
        page_count=1,
    )
    return RawDocument(text=text.strip(), formatting_flags=flags)
