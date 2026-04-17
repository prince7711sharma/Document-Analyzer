from pydantic import BaseModel, Field
from typing import List, Optional

class ExtractedData(BaseModel):
    document_type: str = Field(..., description="Type of document")
    student_name: str = Field(default="", description="Student name if available")
    analysis_note: str = Field(..., description="Brief note about the document")
    key_fields: str = Field(..., description="Important details from document")

class AnalysisResponse(BaseModel):
    status: str = Field(default="success")
    data: dict = Field(..., description="Analyzed document data")

class ErrorResponse(BaseModel):
    status: str = Field(default="error")
    error: str = Field(..., description="Error message")

class DocumentAnalysisResult(BaseModel):
    analysis_summary: str
    extracted_data: ExtractedData
    eligible_courses: List[str]