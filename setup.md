# Application Setup Guide

This guide provides detailed steps on how to set up and run the Automated Bidder Analysis Platform. You can choose between running it locally for development (recommended for quick start) or using Docker for a more consistent and deployable environment.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Git**: For cloning the repository.
    *   [Download Git](https://git-scm.com/downloads)
*   **Python 3.11+**: For local development without Docker.
    *   [Download Python](https://www.python.org/downloads/)
*   **pip**: Python's package installer (usually comes with Python).
*   **Docker Desktop**: (Only if you plan to use Docker) For building and running the application in a containerized environment.
    *   [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   **An API Key for your chosen LLM provider**: You'll need either a Google API Key (for Gemini models) or an OpenAI API Key (for GPT models).
    *   **Google API Key**: [Get a Google API Key](https://ai.google.dev/gemini-api/docs/get-started/python)
    *   **OpenAI API Key**: [Get an OpenAI API Key](https://platform.openai.com/account/api-keys)

## Step 1: Clone the Repository

Open your terminal or command prompt and run the following command to clone the project to your local machine:

```bash
git clone https://github.com/your-username/automated-bidder-analysis-platform.git
cd automated-bidder-analysis-platform
```

(Replace `https://github.com/your-username/automated-bidder-analysis-platform.git` with the actual repository URL if it's different.)

## Step 2: Configure Environment Variables

This application uses environment variables for sensitive information and configuration. A template file `.env.example` is provided.

1.  **Copy the example `.env` file:**

    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file:** Open the newly created `.env` file in a text editor (e.g., `nano .env` or `gedit .env`) and fill in the required values.

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
    # Choose your LLM provider: "gemini" or "openai"
    LLM_PROVIDER="gemini"

    # Your Google API Key for Gemini Models (REQUIRED if LLM_PROVIDER is "gemini")
    # Get it from https://ai.google.dev/gemini-api/docs/get-started/python
    GOOGLE_API_KEY="your-google-api-key"

    # Your OpenAI API Key (REQUIRED if LLM_PROVIDER is "openai")
    # Get it from https://platform.openai.com/account/api-keys
    # Uncomment the line below and replace with your key if using OpenAI
    # OPENAI_API_KEY="your-openai-api-key"

    # Model names. These will be used based on the LLM_PROVIDER setting.
    # For Gemini (used if LLM_PROVIDER="gemini"):
    EXTRACTION_MODEL_NAME="gemini-1.5-flash"
    ANALYSIS_MODEL_NAME="gemini-1.5-pro"

    # For OpenAI (used if LLM_PROVIDER="openai"). Uncomment and set if using OpenAI:
    # EXTRACTION_MODEL_NAME_OPENAI="gpt-3.5-turbo"
    # ANALYSIS_MODEL_NAME_OPENAI="gpt-4o"
    ```

    **Important:**
    *   If you choose `LLM_PROVIDER="gemini"`, you **must** provide your `GOOGLE_API_KEY`.
    *   If you choose `LLM_PROVIDER="openai"`, you **must** uncomment and provide your `OPENAI_API_KEY`.
    *   For local development, `ENV=development` is sufficient, and `GCP_PROJECT_ID` and `GCS_BUCKET_NAME` are not strictly needed as mock storage will be used.

## Option A: Run Locally (for Development - Recommended for Quick Start)

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

## Option B: Run with Docker (for Containerized Development & Deployment)

This option uses Docker to create a consistent environment, which is ideal for both development and preparing for deployment.

### Docker Installation (if not already installed)

If you don't have Docker installed, follow these steps for Ubuntu. For other Linux distributions or OS, please refer to the [official Docker documentation](https://docs.docker.com/engine/install/).

1.  **Uninstall old versions (if any):**

    ```bash
    for pkg in docker.io docker-doc docker-compose docker-compose-v2 containerd runc; do sudo apt remove $pkg;
    ```

2.  **Set up the Docker repository:**

    *   **Remove any existing incorrect Docker repository entries:**

        ```bash
        sudo rm -f /etc/apt/sources.list.d/docker.list
        ```

    *   **Update the `apt` package index:**

        ```bash
        sudo apt update
        ```

    *   **Install necessary packages for `apt` to use a repository over HTTPS:**

        ```bash
        sudo apt install ca-certificates curl gnupg
        ```

    *   **Add Docker's official GPG key:**

        ```bash
        sudo install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        sudo chmod a+r /etc/apt/keyrings/docker.gpg
        ```

    *   **Add the Docker repository to `apt` sources (using `jammy` for Linux Mint 21.x):**

        ```bash
echo \
  "deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  jammy stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        ```

3.  **Install Docker Engine:**

    *   **Update the `apt` package index again (to include Docker's packages):**

        ```bash
        sudo apt update
        ```

    *   **Install Docker Engine, CLI, and Containerd:**

        ```bash
        sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        ```

4.  **Verify Docker installation:**

    Run a simple test to ensure Docker is installed and running correctly:

    ```bash
    sudo docker run hello-world
    ```

    You should see a message similar to "Hello from Docker!" indicating a successful installation.

5.  **Manage Docker as a non-root user (Highly Recommended):**

    By default, you need `sudo` to run Docker commands. To avoid this, add your user to the `docker` group.

    *   **Add your user to the `docker` group:**

        ```bash
sudo usermod -aG docker $USER
        ```

    *   **Apply the new group membership:**

        You need to **log out and log back in** (or restart your system) for the changes to take effect. This is crucial for the group membership to be recognized.

    *   **Verify you can run Docker without `sudo`:**

        After logging back in, open a new terminal and try:

        ```bash
docker run hello-world
        ```

        If it runs successfully without `sudo`, you're all set!

### Running the Application with Docker

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

## Access the Application

Once the application is running (either locally or via Docker), open your web browser and navigate to:

[http://localhost:8000](http://localhost:8000)

You can now upload your bidder PDF files and start the analysis.

## Cleaning Up (Optional)

*   **To stop the Docker container:** Press `Ctrl+C` in the terminal where the container is running. If it's running in detached mode, find its ID (`docker ps`) and then `docker stop <container_id>`.
*   **To remove the Docker image:** `docker rmi bidder-analysis-app`
*   **To deactivate the virtual environment (if running locally):** `deactivate`
*   **To remove the virtual environment folder:** `rm -rf venv` (macOS/Linux) or `rmdir /s /q venv` (Windows)
