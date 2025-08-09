# Project Requirements – AI Procurement Document Analysis (Phase 2 - Full Stack)

## Goal
Design and build a full-stack, production-ready web application that automates the analysis of public procurement documents. The system will provide a user interface for uploading documents and viewing results. The backend will use a two-step AI process for extraction and analysis, serving all data to the frontend via a JSON API.

---

## Scope – Phase 2
- **In-scope (absolutely necessary)**:
  - **React + Vite Frontend**: A single-page application providing a user interface for uploading PDFs and visualizing the analysis results (dashboard, comparison, executive summary).
  - **Cloud Run (FastAPI) API**: Endpoints to init upload, trigger the processing job, check status, and retrieve all results as inline JSON for the frontend.
  - **Cloud Run Job (Python Worker)**: Runs the full processing pipeline (WF-01 → WF-05).
  - **Google Cloud Storage (GCS)**: Store original PDFs and all generated outputs.
  - **Two-Step LLM Integration**:
    - **Extractor Model (Vertex AI Gemini Flash)**: For fast, structured data extraction.
    - **Analysis Model (Vertex AI Gemini Pro)**: For case-wide reasoning and executive summary.
  - **LangChain**: Used in the final analysis step (WF-05b).
  - **Secret Manager**: For all secrets and credentials.

- **Out of scope**: Cloud SQL, Firestore, Pub/Sub, BigQuery, OCR, User Authentication.

---

## Workflows

### WF-01 – Ingest & Parsing
- User uploads PDFs via the web interface, which uses a signed URL provided by the API.
- Files are stored in `raw/{case_id}/`.
- Worker extracts text and stores it in `work/{case_id}/`.

### WF-02 – Extraction (Per-Document)
- Use **Gemini Flash** for structured data extraction.
- Store as `.extraction.json`.

### WF-03 – Rules & Risks
- Apply business rules to extracted data.
- Store as `.risks.json`.

### WF-04 – Comparator
- Aggregate data from all documents.
- Store as `comparison.json`.

### WF-05 – Reporting & Final Analysis
- **WF-05a (Reporting)**: Generate PDF/Sheet reports.
- **WF-05b (Final Analysis)**: Use **LangChain & Gemini Pro** for a final executive summary. Store as `final_analysis.json`.

---

## API Contracts (FastAPI on Cloud Run)

### `POST /upload-init`
- **Input**: `{ "case_id": "string", "filename": "string", ... }`
- **Output**: `{ "signed_url": "..." }`

### `POST /process`
- **Input**: `{ "case_id": "string" }`
- **Output**: `{ "job_id": "..." }`

### `GET /status/{job_id}`
- **Behavior**: Returns job status.

### `GET /result/{case_id}`
- **Behavior**: Returns a single JSON object with the full, combined content of the results, ready for the web frontend.
- **Output Body**: Contains `case_id`, `extractions`, `comparison`, `final_analysis`, and URLs for downloadable reports.
