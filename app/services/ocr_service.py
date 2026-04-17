import base64
import logging
import os
import fitz  # PyMuPDF
from pathlib import Path
from typing import List
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self):
        """Initialize OCR using Groq Vision API (no local models needed)"""
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.vision_model = settings.GROQ_VISION_MODEL
        logger.info(f"✅ OCR Service initialized using Groq Vision ({self.vision_model})")

    def _image_path_to_base64(self, image_path: str) -> tuple[str, str]:
        """Convert image file to base64 string and detect MIME type"""
        ext = Path(image_path).suffix.lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
        mime_type = mime_map.get(ext, "image/jpeg")
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return b64, mime_type

    def _extract_text_via_vision(self, image_path: str) -> str:
        """Send image to Groq Vision model to extract all text"""
        try:
            b64, mime_type = self._image_path_to_base64(image_path)

            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{b64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": (
                                    "You are a precise OCR engine. Extract ALL text visible in this document image. "
                                    "Include every field, label, value, name, number, date, subject, mark, grade, "
                                    "board name, school/college name, roll number, and any other text. "
                                    "Preserve the structure as much as possible. "
                                    "Return ONLY the extracted text, nothing else."
                                )
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            extracted = response.choices[0].message.content.strip()
            logger.info(f"✅ Vision OCR extracted {len(extracted)} characters")
            return extracted

        except Exception as e:
            logger.error(f"❌ Groq Vision OCR failed: {str(e)}")
            raise Exception(f"Vision OCR failed: {str(e)}")

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from a single image file using Groq Vision"""
        logger.info(f"📸 Processing image via Groq Vision: {image_path}")
        return self._extract_text_via_vision(image_path)

    def pdf_to_images(self, pdf_path: str, output_folder: str) -> List[str]:
        """Convert PDF pages to JPEG images using PyMuPDF"""
        try:
            logger.info(f"📄 Converting PDF to images: {pdf_path}")
            pdf_doc = fitz.open(pdf_path)
            image_paths = []
            for i in range(len(pdf_doc)):
                page = pdf_doc.load_page(i)
                # 150 DPI is enough for vision API (saves memory vs 300 DPI)
                pix = page.get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
                img_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
                pix.save(img_path)
                image_paths.append(img_path)
            pdf_doc.close()
            logger.info(f"✅ Converted PDF to {len(image_paths)} page image(s)")
            return image_paths
        except Exception as e:
            logger.error(f"❌ PDF to image conversion failed: {str(e)}")
            raise Exception(f"Unable to convert PDF: {str(e)}")

    def extract_text_from_pdf(self, pdf_path: str, temp_dir: str) -> str:
        """
        Extract text from PDF.
        - First tries PyMuPDF native text extraction (for text-based PDFs).
        - Falls back to Groq Vision (for scanned/image-based PDFs).
        """
        try:
            logger.info(f"📄 Extracting text from PDF: {pdf_path}")
            pdf_doc = fitz.open(pdf_path)

            # --- Attempt 1: Native text extraction (fast, no API call) ---
            native_pages = []
            for i in range(len(pdf_doc)):
                page = pdf_doc.load_page(i)
                text = page.get_text().strip()
                if text:
                    native_pages.append(text)
            pdf_doc.close()

            native_text = "\n\n".join(native_pages).strip()
            if len(native_text) >= 50:
                logger.info(f"✅ Native PDF text extracted ({len(native_text)} chars)")
                return native_text

            # --- Attempt 2: Image-based PDF → Groq Vision ---
            logger.info("🔍 No native text found. Using Groq Vision for scanned PDF...")
            image_paths = self.pdf_to_images(pdf_path, temp_dir)
            page_texts = []

            for img_path in image_paths:
                try:
                    text = self._extract_text_via_vision(img_path)
                    page_texts.append(text)
                except Exception as e:
                    logger.warning(f"⚠️ Vision failed for page {img_path}: {e}")
                finally:
                    try:
                        os.remove(img_path)
                    except Exception:
                        pass

            combined = "\n\n".join(page_texts).strip()
            logger.info(f"✅ Vision OCR complete for PDF ({len(combined)} chars)")
            return combined

        except Exception as e:
            logger.error(f"❌ PDF extraction failed: {str(e)}")
            raise


# Initialize OCR service
ocr_service = OCRService()