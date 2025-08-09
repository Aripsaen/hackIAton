# Project Requirements – AI Procurement Document Analysis (Phase 1 - Revised)

## Goal
Design a minimal, production-ready web application that automates the analysis of public procurement documents. The system will use a two-step AI process: first, fast and cheap extraction of structured data from multiple documents, and second, a holistic, case-wide analysis by a more powerful reasoning model. The system will output structured JSON, risk flags, a comparison matrix, a final executive summary, and a simple PDF report, all accessible via a JSON API designed to feed a web application frontend.

This is **Phase 1 (Hackathon)** — no unnecessary infrastructure. Must be fast to deploy on **Google Cloud Platform (GCP)**.

---

## Scope – Phase 1 (Strict)
- **In-scope (absolutely necessary)**:
  - **Cloud Run (FastAPI) API**: Endpoints to init upload, trigger the processing job, check status, and retrieve all results as inline JSON.
  - **Cloud Run Job (Python Worker)**: Runs the full processing pipeline (WF-01 → WF-05).
  - **Google Cloud Storage (GCS)**: Store original PDFs and all generated outputs (JSON, PDF reports).
  - **Google Sheets + Looker Studio**: Worker writes summary KPIs to a Sheet for a simple, external dashboard.
  - **Two-Step LLM Integration**:
    - **Extractor Model (Vertex AI Gemini Flash)**: For high-speed, low-cost structured data extraction from individual documents.
    - **Analysis Model (Vertex AI Gemini Pro)**: For case-wide reasoning and generating an executive summary. 
  - **LangChain**: Used in the final analysis step (WF-05b) to orchestrate the call to the analysis model.
  - **Secret Manager**: Store LLM API keys, Google Sheets credentials, config values.

- **Out of scope for Phase 1**: Cloud SQL, Firestore, Pub/Sub, BigQuery, OCR.

---

## Workflows

### WF-01 – Ingest & Parsing
- Input: PDFs from user (uploaded via signed URL to GCS).
- Validate and store in GCS: `raw/{case_id}/{original_filename}.pdf`.
- Extract text (no OCR), normalize, and store: `work/{case_id}/{doc_id}.txt`.

### WF-02 – Extraction (Per-Document)
- Load normalized text for each document.
- Use **Gemini Flash** to extract key fields into **normalized JSON**.
- Include provenance and diagnostics.
- Store in GCS: `results/{case_id}/{doc_id}.extraction.json`.

### WF-03 – Rules & Risks
- Apply simple business rules to the extracted JSON from each document.
- Output risk flags.
- Store: `results/{case_id}/{doc_id}.risks.json`.

### WF-04 – Comparator
- Aggregate data from all documents in the same `case_id`.
- Compute KPIs (cumplimiento %, riesgo %, monto).
- Store: `results/{case_id}/comparison.json`.

### WF-05 – Reporting & Final Analysis
- **WF-05a (Reporting)**: 
    - Generate a simple PDF summary of the comparison.
    - Store in GCS: `reports/{case_id}/report.pdf`.
    - Append/update Google Sheet with KPIs.
- **WF-05b (Final Analysis)**:
    - Use **LangChain** to orchestrate a call to the **Gemini Pro** model.
    - Input: The `comparison.json` and the full text of all documents.
    - Output: A final executive summary and risk analysis for the entire case.
    - Store in GCS: `results/{case_id}/final_analysis.json`.

---

## API Contracts (FastAPI on Cloud Run)

### `POST /upload-init`
- **Input**: `{ "case_id": "string", "filename": "string", "content_type": "application/pdf" }`
- **Output**: `{ "signed_url": "...", "gcs_path": "..." }`

### `POST /process`
- **Input**: `{ "case_id": "string" }`
- **Behavior**: Kicks off the Cloud Run Job. Returns `{ "job_id": "..." }`.

### `GET /status/{job_id}`
- **Behavior**: Returns job status using GCS markers.

### `GET /result/{case_id}`
- **Behavior**: Returns a single JSON object containing the **full content** of the results, ready for a web frontend.
- **Output Body**:
```json
{
  "case_id": "string",
  "extractions": [ { ... } ],
  "comparison": { ... },
  "final_analysis": { ... },
  "report_pdf_url": "https://...",
  "sheet_url": "https://..."
}
```