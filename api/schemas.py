from pydantic import BaseModel, Field
from typing import List, Dict, Any

# --- /upload-init ---
class UploadInitPayload(BaseModel):
    case_id: str = Field(..., description="Unique identifier for the case.")
    filename: str = Field(..., description="Original filename of the PDF.")
    content_type: str = Field("application/pdf", description="MIME type of the file.")

class UploadInitResponse(BaseModel):
    signed_url: str = Field(..., description="GCS signed URL for PUT upload.")
    gcs_path: str = Field(..., description="The destination path in GCS.")

# --- /process ---
class ProcessPayload(BaseModel):
    case_id: str = Field(..., description="The case_id to process.")
    doc_ids: List[str] = Field([], description="Optional list of specific doc_ids to process. If empty, all docs in the case are processed.")

class ProcessResponse(BaseModel):
    job_id: str = Field(..., description="A unique identifier for the processing job.")
    status: str = Field("PENDING", description="Initial status of the job.")

# --- /status/{job_id} ---
class StatusResponse(BaseModel):
    job_id: str
    status: str = Field(..., description="Current status: PENDING|RUNNING|SUCCEEDED|FAILED")

# --- /result/{case_id} ---
class ResultResponse(BaseModel):
    case_id: str
    # Return the actual data for the web app frontend
    extractions: List[Dict[str, Any]] = Field(..., description="List of extraction JSONs for each document.")
    comparison: Dict[str, Any] = Field(..., description="The comparison JSON for the case.")
    final_analysis: Dict[str, Any] = Field(..., description="The final, executive analysis JSON for the case.")
    
    # URLs for artifacts that are better downloaded
    report_pdf_url: str = Field(..., description="Signed URL for the summary PDF report.")
    sheet_url: str = Field(..., description="URL to the Google Sheet dashboard.")