import os
import uuid
import logging
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.config import settings

logger = logging.getLogger(__name__)


class FileHandler:
    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """Validate uploaded file"""
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        logger.info(f"✅ File validation passed: {file.filename}")

    @staticmethod
    async def save_temp_file(file: UploadFile) -> str:
        """Save uploaded file temporarily"""
        try:
            # Generate unique filename
            file_ext = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(settings.TEMP_DIR, unique_filename)

            # Save file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            logger.info(f"💾 File saved: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"❌ Failed to save file: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save uploaded file")

    @staticmethod
    def cleanup_file(file_path: str) -> None:
        """Delete temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"🗑️ Cleaned up: {file_path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to cleanup {file_path}: {str(e)}")


file_handler = FileHandler()