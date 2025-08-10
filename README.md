# Automated Bidder Analysis Platform

This project is a full-stack web application designed to automate the analysis and comparison of bidder documents for a hackathon.

## Features

- **PDF Ingestion**: Upload multiple bidder PDF documents via a web interface.
- **Automated Extraction**: Uses Google's Gemini Flash model to extract key information into a structured JSON format.
- **Rubric-Based Analysis**: Uses Google's Gemini Pro model via LangChain to analyze the extracted data against a predefined rubric, generating scores and qualitative feedback.
- **Bidder Comparison**: Aggregates data from all bidders in a "case" to provide a side-by-side comparison.
- **Report Generation**: Creates a final summary report in PDF format.
- **Flexible Storage**: Supports both a local file-based mock for development and Google Cloud Storage for production.
- **Easy Deployment**: Containerized with Docker for simple, one-command setup and execution.

## Technology Stack

- **Backend**: Python 3.11, FastAPI
- **Frontend**: HTML, CSS, JavaScript (no frameworks)
- **LLM Orchestration**: LangChain
- **LLM Models**: Configurable (Google Gemini Pro/Flash, OpenAI GPT models supported via LangChain)
- **PDF Parsing**: `pdfplumber`
- **Report Generation**: `reportlab`
- **Deployment**: Docker

## Project Structure

```
/
|-- app/
|   |-- __init__.py
|   |-- main.py             # FastAPI app definition & endpoints
|   |-- core/
|   |   |-- __init__.py
|   |   |-- config.py         # Configuration loading from .env
|   |   |-- llm.py            # LangChain and Gemini integration
|   |   |-- storage.py        # GCS client (real and mock)
|   |-- services/
|   |   |-- __init__.py
|   |   |-- workflow.py       # All workflow logic (ingest, extract, analyze, etc.)
|   |-- models/
|   |   |-- __init__.py
|   |   |-- schemas.py        # Pydantic models for data structures
|-- static/
|   |-- index.html          # Main frontend page
|   |-- style.css
|   |-- script.js
|-- .env.example            # Example environment variables
|-- requirements.txt        # Python dependencies
|-- Dockerfile              # Docker container definition
|-- README.md
```

## Setup and Running the Application

This section provides detailed instructions on how to set up and run the Automated Bidder Analysis Platform. You can choose between running it locally for development or using Docker for a more consistent and deployable environment.

### Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Git**: For cloning the repository.
    *   [Download Git](https://git-scm.com/downloads)
*   **Python 3.11+**: For local development without Docker.
    *   [Download Python](https://www.python.org/downloads/)
*   **pip**: Python's package installer (usually comes with Python).
*   **Docker Desktop**: For building and running the application in a containerized environment (recommended for both development and deployment).
    *   [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   **An API Key for your chosen LLM provider**: You'll need either a Google API Key (for Gemini models) or an OpenAI API Key (for GPT models).
    *   **Google API Key**: [Get a Google API Key](https://ai.google.dev/gemini-api/docs/get-started/python)
    *   **OpenAI API Key**: [Get an OpenAI API Key](https://platform.openai.com/account/api-keys)

### Step 1: Clone the Repository

Open your terminal or command prompt and run the following command to clone the project to your local machine:

```bash
git clone https://github.com/your-username/automated-bidder-analysis-platform.git
cd automated-bidder-analysis-platform
```

(Replace `https://github.com/your-username/automated-bidder-analysis-platform.git` with the actual repository URL if it's different.)

### Step 2: Configure Environment Variables

This application uses environment variables for sensitive information and configuration. A template file `.env.example` is provided.

1.  **Copy the example `.env` file:**

    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file:** Open the newly created `.env` file in a text editor. You need to fill in the required values.

    ```env
    # Set to "production" to use Google Cloud Storage, otherwise uses local mock storage.
    # For local development, keep this as "development".
    ENV=development

    # Your Google Cloud Project ID (only needed if ENV is "production" and you're using GCS)
    # If you're running locally with mock storage, you can leave this as is.
    GCP_PROJECT_ID="your-gcp-project-id"

    # The GCS bucket name to use (only needed if ENV is "production" and you're using GCS)
    # If you're running locally with mock storage, you can leave this as is.
    GCS_BUCKET_NAME="your-gcs-bucket-name"

    # LLM Configuration
    # Set the provider for the extraction model: "gemini" or "openai"
    EXTRACTION_LLM_PROVIDER="gemini"

    # Set the provider for the analysis model: "gemini" or "openai"
    ANALYSIS_LLM_PROVIDER="gemini"

    # API Keys for specific models/providers
    # If using Gemini, set EXTRACTION_API_KEY and ANALYSIS_API_KEY to your Google API Key.
    # If using OpenAI, set EXTRACTION_API_KEY and ANALYSIS_API_KEY to your OpenAI API Key.
    EXTRACTION_API_KEY="your-extraction-api-key"
    ANALYSIS_API_KEY="your-analysis-api-key"

    # Model names. These will be used based on the LLM_PROVIDER setting.
    # For Gemini:
    EXTRACTION_MODEL_NAME="gemini-1.5-flash"
    ANALYSIS_MODEL_NAME="gemini-1.5-pro"

    # For OpenAI (uncomment and set if using OpenAI):
    # EXTRACTION_MODEL_NAME_OPENAI="gpt-3.5-turbo"
    # ANALYSIS_MODEL_NAME_OPENAI="gpt-4o"

    # Temperature settings for models (0.0 to 1.0)
    EXTRACTION_TEMPERATURE=0.1
    ANALYSIS_TEMPERATURE=0.2
    ```

    **Important:**
    *   For each model (extraction and analysis), ensure you set its `_LLM_PROVIDER` (e.g., `EXTRACTION_LLM_PROVIDER`) to either `"gemini"` or `"openai"`.
    *   Provide the corresponding API key in `EXTRACTION_API_KEY` and `ANALYSIS_API_KEY`. If using Gemini, this will be your Google API Key. If using OpenAI, this will be your OpenAI API Key.
    *   For local development, `ENV=development` is sufficient, and `GCP_PROJECT_ID` and `GCS_BUCKET_NAME` are not strictly needed as mock storage will be used.

### Option A: Run Locally (for Development)

This option is suitable for local development and testing without Docker. You'll need Python and pip installed.

1.  **Create a Python Virtual Environment (Recommended):**

    ```bash
    python3 -m venv venv
    ```

2.  **Activate the Virtual Environment:**

    *   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    *   **On Windows (Command Prompt):**
        ```bash
        venv\Scripts\activate.bat
        ```
    *   **On Windows (PowerShell):**
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```

3.  **Install Python Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the FastAPI Application:**

    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    *   The `--reload` flag is useful for development as it automatically restarts the server when code changes are detected.

### Option B: Run with Docker (Recommended for Development & Deployment)

This option uses Docker to create a consistent environment, which is ideal for both development and preparing for deployment.

1.  **Ensure Docker Desktop is Running:** Make sure the Docker application is open and running on your machine.

2.  **Build the Docker Image:** Navigate to the root directory of the project (where `Dockerfile` is located) in your terminal and run:

    ```bash
    docker build -t bidder-analysis-app .
    ```
    This command builds a Docker image named `bidder-analysis-app` based on the `Dockerfile`.

3.  **Run the Docker Container:**

    *   **For Local Development (with live code changes):**

        ```bash
        docker run -p 8000:8000 -v "$(pwd)":/app --env-file .env bidder-analysis-app
        ```
        *   `-p 8000:8000`: Maps port 8000 on your host machine to port 8000 inside the container.
        *   `-v "$(pwd)":/app`: **(Important for Development)** This mounts your current local project directory into the `/app` directory inside the container. Any changes you make to your local code will be immediately reflected in the running container without needing to rebuild the image.
        *   `--env-file .env`: Passes your `.env` file's environment variables into the container.

    *   **For Deployment (e.g., to a server, without live code changes):**

        For deployment, you typically don't need the volume mount, as the code is already copied into the image during the build process. You might also set `ENV=production` in your `.env` file to enable Google Cloud Storage.

        ```bash
        docker run -p 8000:8000 --env-file .env bidder-analysis-app
        ```
        *   In a real deployment scenario, you would likely use a more robust orchestration tool (like Docker Compose, Kubernetes, or a cloud-specific service) and manage your environment variables more securely.

### Step 3: Access the Application

Once the application is running (either locally or via Docker), open your web browser and navigate to:

[http://localhost:8000](http://localhost:8000)

You can now upload your bidder PDF files and start the analysis.

### Cleaning Up (Optional)

*   **To stop the Docker container:** Press `Ctrl+C` in the terminal where the container is running. If it's running in detached mode, find its ID (`docker ps`) and then `docker stop <container_id>`.
*   **To remove the Docker image:** `docker rmi bidder-analysis-app`
*   **To deactivate the virtual environment (if running locally):** `deactivate`
*   **To remove the virtual environment folder:** `rm -rf venv` (macOS/Linux) or `rmdir /s /q venv` (Windows)
