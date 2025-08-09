# AI Procurement Document Analysis

This project is a minimal, production-ready web application to automate the analysis of public procurement documents using a two-step AI process. It is designed to be the backend for a web application.

1.  **Fast Extraction**: It first uses a fast, efficient model (like Gemini Flash) to extract structured data from multiple PDF documents for a given case.
2.  **Deep Analysis**: After processing all documents, it uses a more powerful reasoning model (like Gemini Pro) to perform a holistic, case-wide analysis, providing an executive summary and identifying key risks.

All results are exposed via a JSON API, ready to be consumed by a front-end.

## Architecture

*   **API Server**: A FastAPI application on **Cloud Run** that exposes endpoints to upload documents, start analysis, and retrieve the final, consolidated JSON results.
*   **Worker**: A Python script running as a **Cloud Run Job** that performs the core analysis pipeline.
*   **Two-Step LLM Process**:
    *   **WF-02 (Extraction)**: Uses **Gemini Flash** for quick, structured data extraction from each PDF.
    *   **WF-05 (Analysis)**: Uses **LangChain** and **Gemini Pro** to perform a final, case-wide analysis based on all extracted data.
*   **Storage (GCS)**: Google Cloud Storage stores all artifacts, including original PDFs, intermediate text, and all resulting JSON files.
*   **Dashboard**: A Google Sheet + Looker Studio provides an optional, simple dashboard for high-level KPI tracking.

## Local Development

### 1. Prerequisites

*   Google Cloud SDK (`gcloud`)
*   Docker
*   Python 3.11+
*   `make`

### 2. Environment Setup

Copy the example environment file and fill in the values for your GCP project.

```bash
cp .env.example .env
```

**Key Variables:**
*   `PROJECT_ID`: Your Google Cloud Project ID.
*   `REGION`: The GCP region (e.g., `us-central1`).
*   `BUCKET_NAME`: Your GCS bucket name.
*   `GOOGLE_SHEET_ID`: The ID of the Google Sheet for the dashboard.
*   `VERTEX_MODEL_NAME`: The model for fast extraction (e.g., `gemini-1.5-flash-001`).
*   `VERTEX_PRO_MODEL_NAME`: The powerful model for final analysis (e.g., `gemini-1.5-pro-001`).
*   `SERVICE_ACCOUNT_FILE`: Path to your GCP service account key for local development.

### 3. Running Locally

**Install dependencies:**
```bash
make install
```

**Run the API server:**
```bash
make run-api
```
The API will be available at `http://127.0.0.1:8000`.

**Run the Worker (example):**
```bash
# Ensure a PDF for the case exists in gs://<your-bucket>/raw/test-case-001/
CASE_ID="test-case-001" python -m worker.run --case_id $CASE_ID
```

## Deployment to Google Cloud

Refer to the `gcloud` commands in `instructions.txt` for deploying the API and Worker to Cloud Run.

## API Endpoint for Frontend

To get the results for a processed case, the frontend can call:

`GET /result/{case_id}`

This endpoint returns a single JSON object containing all the necessary data to render the results page, including the list of extractions, the comparison table, and the final AI-generated analysis.