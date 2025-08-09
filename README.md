# AI Procurement Document Analysis

This project is a minimal, production-ready web application to automate the analysis of public procurement documents using AI. It extracts structured information, detects risks, compares bidders, and generates reports.

This is Phase 1, built for a hackathon, focusing on a lean GCP-native architecture.

## Architecture

- **API Server**: A FastAPI application running on **Cloud Run** that exposes endpoints for uploading documents, starting analysis, checking status, and retrieving results.
- **Worker**: A Python script running as a **Cloud Run Job** that performs the core analysis pipeline (WF-01 to WF-05).
- **Storage**: **Google Cloud Storage (GCS)** is used to store original PDFs, intermediate text files, and all JSON/PDF outputs.
- **Dashboard**: A **Google Sheet** acts as a simple database, updated by the worker. A **Looker Studio** dashboard is built on top of this sheet for visualization.
- **AI/LLM**: **Vertex AI (Gemini)** is the default Large Language Model, with an abstraction layer to support other providers like OpenAI.
- **Secrets**: **Secret Manager** is used for storing API keys and service account credentials.

## Local Development

### 1. Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/install) (`gcloud`)
- [Docker](https://docs.docker.com/get-docker/)
- Python 3.11+
- `make`

### 2. Environment Setup

Copy the example environment file and fill in the values for your GCP project.

```bash
cp .env.example .env
```

**Key Variables:**

- `PROJECT_ID`: Your Google Cloud Project ID.
- `REGION`: The GCP region (e.g., `us-central1`).
- `BUCKET_NAME`: The name of your GCS bucket.
- `GOOGLE_SHEET_ID`: The ID of the Google Sheet for the dashboard.
- `SERVICE_ACCOUNT_FILE`: Path to your GCP service account JSON key file. This is required for local authentication. When deployed on GCP, Workload Identity is recommended.

### 3. Running Locally

You can run the API and Worker services locally using the Makefile.

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
To simulate a worker run, you can execute the `run.py` script directly. First, ensure a PDF exists in the expected GCS path.

```bash
# Example of running the worker for a specific case
CASE_ID="test-case-001" python worker/run.py --case_id $CASE_ID
```

## Frontend (React Dashboard)

The project includes a React-based web dashboard for a complete user experience.

### Prerequisites for Frontend

- [Node.js](https://nodejs.org/) 16+ and npm
- The API server must be running on `http://localhost:8000`

### Setup and Run Frontend

1. **Navigate to the frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Start the development server:**

   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173` (or another port if 5173 is busy).

### Frontend Features

The dashboard provides three main sections:

- **📁 Cargar Documentos**: Upload PDF documents (pliegos, propuestas, contratos) for analysis
- **📊 Dashboard**: View analysis results, risk assessment, and document classification
- **⚖️ Comparación**: Compare multiple bidders side-by-side with objective metrics

### Important Notes

- The frontend is configured to connect to the API at `http://localhost:8000`
- Make sure the API server is running before using the frontend
- The frontend will automatically handle file uploads, processing status, and results display
- All uploaded files are processed through the complete AI pipeline (WF-01 to WF-05)

## Docker

Build Docker images for the API and the worker.

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"

# Build API image
make build-api-docker

# Build Worker image
make build-worker-docker
```

Push the images to Google Artifact Registry:

```bash
# Authenticate Docker with gcloud
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Push API image
make push-api-docker

# Push Worker image
make push-worker-docker
```

## Deployment to Google Cloud

### 1. Deploy the API (Cloud Run Service)

```bash
gcloud run deploy api-procurement \
  --source . \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars "PROJECT_ID=${PROJECT_ID},BUCKET_NAME=${BUCKET_NAME},GOOGLE_SHEET_ID=${GOOGLE_SHEET_ID}" \
  --service-account "your-service-account-email" # Recommended: Use a dedicated SA with Workload Identity
```

### 2. Deploy the Worker (Cloud Run Job)

```bash
gcloud run jobs deploy worker-procurement \
  --source . \
  --platform managed \
  --region ${REGION} \
  --set-env-vars "PROJECT_ID=${PROJECT_ID},BUCKET_NAME=${BUCKET_NAME},GOOGLE_SHEET_ID=${GOOGLE_SHEET_ID}" \
  --service-account "your-service-account-email" \
  --task-timeout 3600 # 1 hour
```

### 3. Trigger a Job

You can trigger the worker job via the API's `/process` endpoint or directly using `gcloud`.

```bash
# Trigger via gcloud
gcloud run jobs execute worker-procurement --region ${REGION} --args "--case_id=your-case-id"
```

## Looker Studio Dashboard Setup

1.  **Create a Google Sheet**: Create a new Google Sheet and get its ID from the URL.
2.  **Share the Sheet**: Share the Google Sheet with the service account email you are using for the Cloud Run services, giving it "Editor" permissions.
3.  **Create a Looker Studio Report**:
    - Go to [Looker Studio](https://lookerstudio.google.com/).
    - Create a new **Blank Report**.
    - When prompted to add data, select the **Google Sheets** connector.
    - Find and select the sheet you created. Ensure "Use first row as headers" and "Include hidden and filtered cells" are checked.
    - Click **Add**.
4.  **Build Your Dashboard**: Drag and drop charts (e.g., tables, scorecards) and configure them to display the columns from your sheet (`cumplimiento`, `riesgo`, `monto`, etc.).
