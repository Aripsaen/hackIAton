from pydantic import BaseModel, Field
from typing import List, Dict, Any

# --- API Schemas ---
# Payloads for initiating uploads and processing
class UploadInitPayload(BaseModel):
    case_id: str
    filename: str
    content_type: str = "application/pdf"

class UploadInitResponse(BaseModel):
    signed_url: str
    gcs_path: str

class ProcessPayload(BaseModel):
    case_id: str

class ProcessResponse(BaseModel):
    job_id: str
    status: str

class StatusResponse(BaseModel):
    job_id: str
    status: str

# --- Result Schemas ---
# This is the main schema for the GET /result/{case_id} endpoint.
# It's designed to provide all necessary data to the frontend in one call.

class ResultResponse(BaseModel):
    case_id: str
    # The comparison object now contains the bidders with their KPIs and nested analysis.
    comparison: Dict[str, Any] = Field(..., description="The comparison JSON for the case, including bidders and their individual analyses.")
    
    # URLs for artifacts that are better downloaded
    report_pdf_url: str = Field(..., description="Signed URL for the summary PDF report.")
    sheet_url: str = Field(..., description="URL to the Google Sheet dashboard.")
