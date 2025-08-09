# AI Procurement Document Analysis - Full Stack

This project is a full-stack web application that automates the analysis of public procurement documents using a two-step AI process. It features a React-based frontend and a Python/FastAPI backend.

1.  **Upload**: The user uploads multiple PDF documents for a specific case through the web interface.
2.  **Fast Extraction**: The backend uses a fast, efficient model (Gemini Flash) to extract structured data from each document.
3.  **Deep Analysis**: After processing, a more powerful reasoning model (Gemini Pro) performs a holistic, case-wide analysis, providing an executive summary and identifying key risks.
4.  **Visualize**: All results are sent to the frontend in a single API call and displayed in a dashboard with summary cards, a comparison table, and the final AI analysis.

## Architecture

*   **Frontend**: A **React (Vite)** single-page application that provides the user interface. It communicates with the backend API to upload files and display results.
*   **API Server**: A **FastAPI** application on Cloud Run that serves the frontend (or handles its requests via CORS) and manages the analysis workflow.
*   **Worker**: A Python script running as a **Cloud Run Job** that performs the core AI analysis pipeline.
*   **Two-Step LLM Process**: Uses Gemini Flash for extraction and Gemini Pro (via LangChain) for the final analysis.
*   **Storage (GCS)**: Stores all documents and JSON artifacts.

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
    # Install Python dependencies
    make install

    # Run the FastAPI server
    make run-api
    ```

2.  **Terminal 2: Run the Frontend**
    ```bash
    # Navigate to the frontend directory
    cd frontend

    # Install Node.js dependencies
    npm install

    # Start the Vite development server
    npm run dev
    ```

3.  **Access the Application**: Open your browser to the address provided by the Vite server (usually `http://localhost:5173`).

## Deployment

The backend API and the worker can be deployed to Cloud Run using the `gcloud` commands in `instructions.txt`. The frontend can be built into static files (`npm run build`) and served from any static hosting provider, like Firebase Hosting or a GCS bucket, configured to point to the deployed API URL.