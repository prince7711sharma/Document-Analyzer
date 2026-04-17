import easyocr
import logging
from PIL import Image
import fitz  # PyMuPDF
from typing import List
import os

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self):
        """Initialize EasyOCR reader"""
        try:
            logger.info("🔄 Initializing OCR Engine (EasyOCR)...")
            logger.info("📡 Checking for OCR models. This may take a moment on first run...")
            
            # Initialize reader
            self.reader = easyocr.Reader(['en'], gpu=False)
            
            logger.info("✨ OCR Engine ready. Using CPU mode (Note: GPU is faster if available)")
            logger.info("✅ EasyOCR initialized successfully")
        except Exception as e:
            logger.error("❌ Failed to initialize EasyOCR. Check if models can be downloaded.")
            logger.error(f"Error Details: {str(e)}")
            raise

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from a single image"""
        try:
            logger.info(f"📄 Extracting text from image: {image_path}")

            # Read image and extract text
            result = self.reader.readtext(image_path, detail=0, paragraph=True)

            # Combine all text
            text = " ".join(result)

            logger.info(f"✅ Extracted {len(text)} characters")
            return text.strip()

        except Exception as e:
            logger.error(f"❌ OCR extraction failed: {str(e)}")
            raise Exception(f"Unable to extract text from image: {str(e)}")

    def pdf_to_images(self, pdf_path: str, output_folder: str) -> List[str]:
        """Convert PDF pages to images using PyMuPDF (no Poppler needed!)"""
        try:
            logger.info(f"📄 Converting PDF to images: {pdf_path}")
            pdf_doc = fitz.open(pdf_path)
            image_paths = []
            for i in range(len(pdf_doc)):
                page = pdf_doc.load_page(i)
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                image_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
                pix.save(image_path)
                image_paths.append(image_path)
            pdf_doc.close()
            logger.info(f"✅ Converted PDF to {len(image_paths)} images")
            return image_paths
        except Exception as e:
            logger.error(f"❌ PDF conversion failed: {str(e)}")
            raise Exception(f"Unable to convert PDF to images: {str(e)}")

    def extract_text_from_pdf(self, pdf_path: str, temp_dir: str) -> str:
        """Extract text from PDF by converting to images first"""
        try:
            # Convert PDF to images
            image_paths = self.pdf_to_images(pdf_path, temp_dir)

            # Extract text from each image
            all_text = []
            for img_path in image_paths:
                text = self.extract_text_from_image(img_path)
                all_text.append(text)

                # Clean up temporary image
                try:
                    os.remove(img_path)
                except:
                    pass

            # Combine all text
            combined_text = "\n\n".join(all_text)
            return combined_text.strip()

        except Exception as e:
            logger.error(f"❌ PDF text extraction failed: {str(e)}")
            raise


# Initialize OCR service
ocr_service = OCRService()