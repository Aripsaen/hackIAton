import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import run_v2

from . import schemas, gcs, config

app = FastAPI(title="AI Procurement Analysis API")

# CORS Configuration
origins = config.settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
def read_root():
    return {"status": "ok"}

@app.post("/upload-init", response_model=schemas.UploadInitResponse, tags=["Upload"])
def initialize_upload(payload: schemas.UploadInitPayload):
    '''
    Generates a signed URL for a client to upload a PDF to GCS.
    '''
    try:
        gcs_path = f"raw/{payload.case_id}/{payload.filename}"
        signed_url = gcs.generate_signed_url_for_upload(
            bucket_name=config.settings.BUCKET_NAME,
            blob_name=gcs_path,
            content_type=payload.content_type,
        )
        return schemas.UploadInitResponse(signed_url=signed_url, gcs_path=gcs_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate signed URL: {e}")

def run_cloud_run_job(case_id: str):
    '''Helper to trigger the Cloud Run Job.'''
    client = run_v2.JobsClient()
    job_name = f"projects/{config.settings.PROJECT_ID}/locations/{config.settings.REGION}/jobs/worker-procurement"
    
    request = run_v2.RunJobRequest(
        name=job_name,
        overrides={
            "container_overrides": [
                {
                    "args": [f"--case_id={case_id}"],
                }
            ]
        },
    )
    operation = client.run_job(request=request)
    return operation.metadata.name


@app.post("/process", response_model=schemas.ProcessResponse, tags=["Processing"])
async def process_documents(payload: schemas.ProcessPayload, background_tasks: BackgroundTasks):
    '''
    Kicks off the Cloud Run Job to process all documents for a given case_id.
    '''
    try:
        # Use background task to avoid long waits, though Cloud Run Job execution is async anyway
        background_tasks.add_task(run_cloud_run_job, payload.case_id)
        # A more robust implementation would return the job ID from the run_job call
        job_id = f"job_for_{payload.case_id}" # Placeholder
        gcs.create_gcs_marker(config.settings.BUCKET_NAME, f"work/{payload.case_id}/_JOB_{job_id}.pending")
        return schemas.ProcessResponse(job_id=job_id, status="PENDING")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start processing job: {e}")


@app.get("/status/{job_id}", response_model=schemas.StatusResponse, tags=["Processing"])
def get_job_status(job_id: str):
    '''
    Checks the status of a job using GCS markers.
    This is a simplified stub. A real implementation would query the Cloud Run API.
    '''
    case_id = job_id.replace("job_for_", "") # Reverse placeholder logic
    bucket_name = config.settings.BUCKET_NAME
    
    if gcs.check_gcs_marker(bucket_name, f"work/{case_id}/_JOB_{job_id}.done"):
        return schemas.StatusResponse(job_id=job_id, status="SUCCEEDED")
    if gcs.check_gcs_marker(bucket_name, f"work/{case_id}/_JOB_{job_id}.error"):
        return schemas.StatusResponse(job_id=job_id, status="FAILED")
    if gcs.check_gcs_marker(bucket_name, f"work/{case_id}/_JOB_{job_id}.running"):
        return schemas.StatusResponse(job_id=job_id, status="RUNNING")
    if gcs.check_gcs_marker(bucket_name, f"work/{case_id}/_JOB_{job_id}.pending"):
        return schemas.StatusResponse(job_id=job_id, status="PENDING")
        
    return schemas.StatusResponse(job_id=job_id, status="UNKNOWN")


@app.get("/result/{case_id}", response_model=schemas.ResultResponse, tags=["Results"])
def get_results(case_id: str):
    '''
    Returns signed URLs for all result artifacts and an inline JSON summary.
    '''
    try:
        results = gcs.get_case_results(config.settings.BUCKET_NAME, case_id, config.settings.GOOGLE_SHEET_ID)
        return results
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Results not found for this case_id.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {e}")
