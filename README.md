# AI Procurement Document Analysis - Full Stack

This project is a full-stack web application that automates the analysis of public procurement documents using a two-step AI process. It features a React-based frontend and a Python/FastAPI backend.

## Core Process

1.  **Upload**: The user uploads multiple PDF documents for a specific case through the web interface.
2.  **Extraction (LLM 1)**: The backend uses a fast model (Gemini Flash) to extract a deeply nested, structured JSON from each document.
3.  **Analysis (LLM 2)**: Immediately following extraction, a powerful reasoning model (Gemini Pro) evaluates each document's structured data against a detailed rubric, producing scores and qualitative feedback.
4.  **Comparison**: The system aggregates the data and scores from all documents to calculate final KPIs.
5.  **Visualize**: All results are served to the frontend, which displays a detailed rubric analysis for each document and a high-level comparison table of all bidders.

## Architecture

*   **Frontend**: A **React (Vite)** application featuring:
    *   A `Dashboard` view that embeds a new `RubricAnalysis` component for each document, showing the detailed AI evaluation.
    *   A `Comparison` view that provides a high-level summary table of the calculated KPIs for each bidder.
*   **API Server**: A **FastAPI** application on Cloud Run that manages the workflow and serves the final, consolidated `comparison.json` to the frontend.
*   **Worker**: A **Cloud Run Job** that performs the re-orchestrated pipeline: Ingest -> Extract -> Analyze -> Compare -> Report.
*   **Two-Step LLM Process**: Uses Gemini Flash for extraction and Gemini Pro (via LangChain) for the rubric-based analysis.

## Local Development

Running the full-stack application locally requires running the backend API and the frontend development server concurrently.

### 1. Prerequisites

*   Google Cloud SDK (`gcloud`)
*   Docker
*   Python 3.11+
*   Node.js v18+ and npm
*   `make`

### 2. Environment Setup

*   **Backend**: Copy `.env.example` to `.env` and fill in your GCP project details, including `VERTEX_MODEL_NAME` and `VERTEX_PRO_MODEL_NAME`.
*   **Frontend**: The frontend is configured to connect to the API at `http://localhost:8000` by default.

### 3. Running Locally

1.  **Terminal 1: Run the Backend API**
    ```bash
    make install && make run-api
    ```

2.  **Terminal 2: Run the Frontend**
    ```bash
    cd frontend && npm install && npm run dev
    ```

3.  **Access the Application**: Open your browser to the address provided by the Vite server (usually `http://localhost:5173`).

## Deployment

The backend API and the worker can be deployed to Cloud Run. The frontend can be built into static files (`npm run build`) and served from any static hosting provider, like Firebase Hosting or a GCS bucket.
