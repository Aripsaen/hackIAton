# Project Requirements – AI Procurement Document Analysis (Phase 1 – Hackathon)

## Goal
Design a minimal, production-ready web application that automates the analysis of public procurement documents (pliegos, propuestas, contratos) using AI.  
The system will extract structured information with provenance, detect risks, compare multiple bidders, and output results via JSON, PDF, and a simple dashboard.

This is **Phase 1 (Hackathon)** — no unnecessary infrastructure.  
Must be fast to deploy on **Google Cloud Platform (GCP)**.

---

## Scope – Phase 1 (Strict)
- **In-scope (absolutely necessary)**:
  - **Cloud Run (FastAPI)** API for:
    - Init upload (Signed URLs to GCS)
    - Process documents (trigger worker)
    - Check status
    - Retrieve results
  - **Cloud Run Job (Python Worker)**:
    - Runs WF-01 → WF-05 in one job
  - **Google Cloud Storage (GCS)**:
    - Store original PDFs and generated outputs (JSON, PDF reports)
  - **Google Sheets + Looker Studio**:
    - Worker writes summary KPIs to Sheet
    - Looker dashboard visualizes data
  - **LLM Integration**:
    - Default: Vertex AI (Gemini)
    - Abstraction layer for switching to external providers (OpenAI, Anthropic, etc.)
  - **Secret Manager**:
    - Store LLM API keys, Google Sheets credentials, config values

- **Out of scope for Phase 1**:
  - Cloud SQL
  - Firestore
  - Pub/Sub
  - BigQuery
  - OCR

---

## Workflows

### WF-01 – Ingest & Parsing
- Input: PDF from user (uploaded via signed URL to GCS)
- Validate type and size
- Store in GCS: `raw/{case_id}/{original_filename}.pdf`
- Extract text (no OCR)
- Normalize and chunk (deterministic)
- Optionally store intermediate: `work/{case_id}/{doc_id}.txt`

### WF-02 – Classification & Extraction
- Load normalized text
- Prompt LLM to extract key fields into **normalized JSON**
- Include:
  - Provenance: `campo`, `evidencia`, `start_char`, `end_char`
  - `diagnostics.missing` for empty/zero fields
- Store in GCS: `results/{case_id}/{doc_id}.extraction.json`

### WF-03 – Rules & Risks
- Apply simple business rules
- Examples:
  - Missing guarantees
  - Ambiguous payment terms
- Output risk flags
- Store: `results/{case_id}/{doc_id}.risks.json`

### WF-04 – Comparator
- Aggregate multiple offers for the same `case_id`
- Compute KPIs (cumplimiento %, riesgo %, monto)
- Store: `results/{case_id}/comparison.json`

### WF-05 – Reports & Dashboard
- Generate PDF summary with:
  - KPIs table
  - Risk flags
- Store in GCS: `reports/{case_id}/report.pdf`
- Append/update Google Sheet:
  - One row per bidder with KPIs, flags, link to report
- Looker Studio dashboard reads from this Sheet

---

## API Contracts (FastAPI on Cloud Run)

### `POST /upload-init`
- **Input**:
```json
{ "case_id": "string", "filename": "string", "content_type": "application/pdf" }
