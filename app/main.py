import logging
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config import settings
from app.models.schemas import AnalysisResponse, ErrorResponse
from app.services.ocr_service import ocr_service
from app.services.ai_service import ai_service
from app.utils.file_handler import file_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="🎓 AI-Powered Document Analyzer API for R.S Education Solution",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS — allow all origins so your website can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """API status endpoint"""
    return {
        "status": "online",
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "endpoint": "/analyze-document"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "groq_configured": bool(settings.GROQ_API_KEY)
    }


@app.post(
    "/analyze-document",
    response_model=AnalysisResponse,
    responses={
        200: {"description": "Document analyzed successfully"},
        400: {"description": "Invalid file or request"},
        500: {"description": "Internal server error"}
    }
)
async def analyze_document(file: UploadFile = File(...)):
    """
    Analyze student academic documents (marksheets, certificates).
    Accepts: JPG, JPEG, PNG, PDF (max 10MB)
    """
    temp_file_path = None
    try:
        logger.info(f"📥 Received file: {file.filename}")
        file_handler.validate_file(file)
        temp_file_path = await file_handler.save_temp_file(file)

        file_ext = Path(file.filename).suffix.lower()
        if file_ext == ".pdf":
            extracted_text = ocr_service.extract_text_from_pdf(temp_file_path, settings.TEMP_DIR)
        else:
            extracted_text = ocr_service.extract_text_from_image(temp_file_path)

        if not extracted_text or len(extracted_text.strip()) < 10:
            return ErrorResponse(error="Unable to extract text. Ensure the document image is clear.").model_dump()

        analysis_result = ai_service.analyze_document(extracted_text)
        return AnalysisResponse(status="success", data=analysis_result).model_dump()

    except Exception as e:
        logger.error(f"❌ Error during analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
    finally:
        if temp_file_path:
            file_handler.cleanup_file(temp_file_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)