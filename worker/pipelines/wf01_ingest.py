from ..utils import gcs, pdf, text, config
import os

def run(case_id: str) -> list[dict]:
    '''
    WF-01: Ingest & Parsing
    - Lists PDFs in the 'raw/{case_id}' GCS directory.
    - For each PDF:
        - Generates a stable doc_id.
        - Downloads, extracts text, and normalizes it.
        - Saves the normalized text to 'work/{case_id}/{doc_id}.txt'.
    - Returns a list of document metadata dictionaries for the next step.
    '''
    print(f"WF-01: Looking for PDFs in gs://{config.settings.BUCKET_NAME}/raw/{case_id}/")
    
    raw_blobs = gcs.list_blobs_in_prefix(f"raw/{case_id}/")
    documents = []

    for blob in raw_blobs:
        if not blob.name.lower().endswith(".pdf"):
            continue

        original_filename = os.path.basename(blob.name)
        # Generate a stable, filesystem-friendly doc_id from the filename
        doc_id = text.filename_to_doc_id(original_filename)
        print(f"  Processing {original_filename} -> doc_id: {doc_id}")

        # Download PDF to a temporary file
        with gcs.download_blob_to_tempfile(blob) as temp_pdf_path:
            # Extract text using PyMuPDF
            raw_text = pdf.extract_text_from_pdf(temp_pdf_path)

        # Normalize text (e.g., remove extra whitespace)
        normalized_text = text.normalize_text(raw_text)

        # Store the normalized text in GCS for provenance and debugging
        work_path = f"work/{case_id}/{doc_id}.txt"
        gcs.upload_content(work_path, normalized_text, "text/plain")
        
        documents.append({
            "case_id": case_id,
            "doc_id": doc_id,
            "original_filename": original_filename,
            "normalized_text_gcs_path": work_path,
            "text_content": normalized_text,
        })

    print(f"WF-01: Found and processed {len(documents)} documents.")
    return documents
