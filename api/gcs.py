import datetime
import json
import os
from google.cloud import storage
from . import config, schemas

def get_gcs_client():
    """Initializes and returns a GCS client."""
    if config.settings.SERVICE_ACCOUNT_FILE and os.path.exists(config.settings.SERVICE_ACCOUNT_FILE):
        return storage.Client.from_service_account_json(config.settings.SERVICE_ACCOUNT_FILE)
    return storage.Client()

def generate_signed_url_for_upload(bucket_name: str, blob_name: str, content_type: str) -> str:
    """Generates a v4 signed URL for uploading a file."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=15),
        method="PUT",
        content_type=content_type,
    )
    return url

def generate_signed_url_for_download(bucket_name: str, blob_name: str) -> str:
    """Generates a v4 signed URL for downloading a file."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(hours=1),
        method="GET",
    )
    return url

def get_case_results(bucket_name: str, case_id: str, sheet_id: str) -> schemas.ResultResponse:
    """Fetches all result artifacts for a case and packages them for the frontend."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    
    base_prefix = f"results/{case_id}/"
    blobs = client.list_blobs(bucket_name, prefix=base_prefix)

    extractions_data = []
    comparison_data = {}
    final_analysis_data = {}
    report_pdf_url = ""

    # Load the JSON content directly from GCS blobs
    for blob in blobs:
        if blob.name.endswith(".extraction.json"):
            extractions_data.append(json.loads(blob.download_as_text()))
        elif blob.name.endswith("comparison.json"):
            comparison_data = json.loads(blob.download_as_text())
        elif blob.name.endswith("final_analysis.json"):
            final_analysis_data = json.loads(blob.download_as_text())

    # Get a signed URL for the PDF report
    report_blob_name = f"reports/{case_id}/report.pdf"
    if bucket.blob(report_blob_name).exists():
        report_pdf_url = generate_signed_url_for_download(bucket_name, report_blob_name)

    if not extractions_data and not comparison_data:
        raise FileNotFoundError("Core result files not found for this case.")

    return schemas.ResultResponse(
        case_id=case_id,
        extractions=extractions_data,
        comparison=comparison_data,
        final_analysis=final_analysis_data,
        report_pdf_url=report_pdf_url,
        sheet_url=f"https://docs.google.com/spreadsheets/d/{sheet_id}"
    )

def create_gcs_marker(bucket_name: str, marker_path: str):
    """Creates an empty file in GCS to act as a status marker."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(marker_path)
    blob.upload_from_string("")

def check_gcs_marker(bucket_name: str, marker_path: str) -> bool:
    """Checks if a GCS marker file exists."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    return storage.Blob(bucket=bucket, name=marker_path).exists(client)