from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import os
import uuid

from app.services.workflow import process_document_workflow, get_comparison_report, generate_report_pdf, get_case_status, update_document_status, get_all_cases_summary, TEMP_DIR
from app.models.schemas import UploadResponse, ComparisonResult, CaseListResponse, CaseSummary

app = FastAPI(
    title="Automated Bidder Analysis Platform",
    description="API for ingesting, analyzing, and comparing bidder documents."
)

# Mount static files for the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serves the main frontend application page."""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/upload/{case_id}", response_model=List[UploadResponse])
async def upload_documents(
    case_id: str,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """WF-01: Uploads PDF documents, triggers text extraction and LLM processing.
    Each uploaded document will be processed in the background.
    """
    responses = []
    for file in files:
        doc_id = str(uuid.uuid4())
        file_content = await file.read()
        
        # Update status to processing immediately
        update_document_status(case_id, doc_id, "processing", file.filename)

        background_tasks.add_task(
            process_document_workflow,
            case_id,
            doc_id,
            file_content,
            file.filename
        )
        responses.append(UploadResponse(message="File uploaded and processing started", case_id=case_id, doc_id=doc_id))
    return responses

@app.get("/api/cases", response_model=CaseListResponse)
async def list_cases():
    """Lists all active cases and their processing status."""
    cases_summary = get_all_cases_summary()
    return CaseListResponse(cases=cases_summary)

@app.get("/api/cases/{case_id}/status", response_model=CaseSummary)
async def get_case_processing_status(case_id: str):
    """Retrieves the processing status for a specific case."""
    status = get_case_status(case_id)
    if status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseSummary(
        case_id=case_id,
        document_count=len(status["documents"]),
        status=status["status"]
    )

@app.get("/api/cases/{case_id}/comparison", response_model=ComparisonResult)
async def get_comparison(case_id: str):
    """WF-04: Retrieves the aggregated comparison report for a given case ID.
    This endpoint will trigger the comparison logic if not already done.
    """
    try:
        comparison_data = await get_comparison_report(case_id)
        return comparison_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating comparison: {e}")

@app.get("/api/cases/{case_id}/report", response_class=FileResponse)
async def get_report(case_id: str):
    """WF-05: Generates and returns a PDF report for a given case ID.
    This endpoint will trigger the report generation logic if not already done.
    """
    try:
        report_path = await generate_report_pdf(case_id)
        return FileResponse(report_path, media_type="application/pdf", filename=f"{case_id}_report.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {e}")

@app.on_event("startup")
async def startup_event():
    # Ensure temp directory exists on startup
    os.makedirs(TEMP_DIR, exist_ok=True)

@app.on_event("shutdown")
async def shutdown_event():
    # Clean up temp directory on shutdown (optional, for development)
    import shutil
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    print(f"Cleaned up temporary directory: {TEMP_DIR}")
