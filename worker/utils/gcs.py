import os
import tempfile
from google.cloud import storage
from . import config

def get_gcs_client():
    '''Initializes and returns a GCS client.'''
    if config.settings.SERVICE_ACCOUNT_FILE and os.path.exists(config.settings.SERVICE_ACCOUNT_FILE):
        return storage.Client.from_service_account_json(config.settings.SERVICE_ACCOUNT_FILE)
    return storage.Client()

def list_blobs_in_prefix(prefix: str) -> list[storage.Blob]:
    '''Lists all blobs in a given GCS prefix.'''
    client = get_gcs_client()
    blobs = client.list_blobs(config.settings.BUCKET_NAME, prefix=prefix)
    return list(blobs)

def download_blob_to_tempfile(blob: storage.Blob) -> tempfile.NamedTemporaryFile:
    '''Downloads a blob to a temporary file and returns the file handle.'''
    _, temp_local_filename = tempfile.mkstemp()
    blob.download_to_filename(temp_local_filename)
    return temp_local_filename

def upload_content(gcs_path: str, content: str | bytes, content_type: str):
    '''Uploads string or bytes content to a GCS path.'''
    client = get_gcs_client()
    bucket = client.bucket(config.settings.BUCKET_NAME)
    blob = bucket.blob(gcs_path)
    blob.upload_from_string(content, content_type=content_type)

def update_job_status(bucket_name: str, case_id: str, job_id: str, status: str):
    '''Updates the job status by creating/deleting GCS marker files.'''
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    
    # Clean up old markers
    for s in ["pending", "running", "done", "error"]:
        old_marker = bucket.blob(f"work/{case_id}/_JOB_{job_id}.{s}")
        if old_marker.exists():
            old_marker.delete()
            
    # Create new marker
    new_marker_path = f"work/{case_id}/_JOB_{job_id}.{status}"
    marker_blob = bucket.blob(new_marker_path)
    marker_blob.upload_from_string("")
    print(f"  Updated job status to '{status}' at gs://{bucket_name}/{new_marker_path}")
