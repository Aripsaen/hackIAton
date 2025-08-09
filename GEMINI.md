# Project Requirements – AI Procurement Document Analysis (Phase 2 - Full Stack)

## Goal
Design and build a full-stack, production-ready web application that automates the analysis of public procurement documents. The system will provide a user interface for uploading documents and viewing results. The backend will use a two-step AI process for extraction and analysis, serving all data to the frontend via a JSON API.

---

## Scope – Phase 2
- **In-scope (absolutely necessary)**:
  - **React + Vite Frontend**: A single-page application providing a user interface for uploading documents and visualizing the analysis results.
  - **Cloud Run (FastAPI) API**: Endpoints to manage the workflow and retrieve all results as a single, consolidated JSON object.
  - **Cloud Run Job (Python Worker)**: Runs the full processing pipeline.
  - **Two-Step LLM Integration**:
    - **Extractor Model (Gemini Flash)**: For structured data extraction.
    - **Analysis Model (Gemini Pro)**: For rubric-based scoring and qualitative analysis on each document.
  - **LangChain**: Used in the analysis step (WF-03).

---

## Workflows (Re-orchestrated)

### WF-01 – Ingest & Parsing
- User uploads PDFs; text is extracted and stored in GCS.

### WF-02 – Extraction (Per-Document)
- Use **Gemini Flash** to extract a detailed, nested JSON structure from each document.
- Store as `results/{case_id}/{doc_id}.extraction.json`.

### WF-03 – Analysis (Per-Document)
- Use **LangChain and Gemini Pro** to perform a rubric-based evaluation on each extracted JSON.
- This generates scores and qualitative feedback for every document.
- Store as `results/{case_id}/{doc_id}.analysis.json`.

### WF-04 – Comparator
- Aggregate data from both the extractions (e.g., `oferta.montoOfertado`) and the analyses (e.g., `totalPuntuacion`).
- Compute final KPIs and create a comprehensive `comparison.json` object that contains all bidder data, KPIs, and their nested analysis results.

### WF-05 – Reporting
- Generate PDF/Sheet reports from the final `comparison.json` data.

---

## API Contracts (FastAPI on Cloud Run)

### `GET /result/{case_id}`
- **Behavior**: Returns a single JSON object containing the final `comparison.json` artifact. This object is the single source of truth for the frontend and contains all necessary data, including the list of bidders, their KPIs, and their individual rubric analyses.
- **Output Body**: 
```json
{
  "case_id": "...",
  "comparison": { 
    "case_id": "...",
    "bidders": [
      {
        "doc_id": "...",
        "name": "...",
        "kpis": { ... },
        "analysis": { ... } // The full rubric analysis is nested here
      }
    ],
    "summary": { ... }
  },
  "report_pdf_url": "...",
  "sheet_url": "..."
}
```