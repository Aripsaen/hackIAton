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
    url = blob.generate_signed_url(version="v4", expiration=datetime.timedelta(minutes=15), method="PUT", content_type=content_type)
    return url

def generate_signed_url_for_download(bucket_name: str, blob_name: str) -> str:
    """Generates a v4 signed URL for downloading a file."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(version="v4", expiration=datetime.timedelta(hours=1), method="GET")
    return url

def get_case_results(bucket_name: str, case_id: str, sheet_id: str) -> schemas.ResultResponse:
    """Fetches the primary comparison artifact for a case and packages it for the frontend."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    
    # The primary artifact is now comparison.json, which contains all other relevant data.
    comparison_blob_name = f"results/{case_id}/comparison.json"
    comparison_blob = bucket.blob(comparison_blob_name)

    if not comparison_blob.exists():
        raise FileNotFoundError(f"comparison.json not found for case {case_id}.")

    comparison_data = json.loads(comparison_blob.download_as_text())

    # Get a signed URL for the PDF report
    report_pdf_url = ""
    report_blob_name = f"reports/{case_id}/report.pdf"
    if bucket.blob(report_blob_name).exists():
        report_pdf_url = generate_signed_url_for_download(bucket_name, report_blob_name)

    return schemas.ResultResponse(
        case_id=case_id,
        comparison=comparison_data,
        report_pdf_url=report_pdf_url,
        sheet_url=f"https://docs.google.com/spreadsheets/d/{sheet_id}"
    )

def create_gcs_marker(bucket_name: str, marker_path: str):
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(marker_path)
    blob.upload_from_string("")

def check_gcs_marker(bucket_name: str, marker_path: str) -> bool:
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    return storage.Blob(bucket=bucket, name=marker_path).exists(client)
