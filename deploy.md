# Deploying the Automated Bidder Analysis Platform to Google Cloud Run

## Prerequisites:

1.  **Google Cloud Account:** Make sure you have an active GCP account.
2.  **Google Cloud SDK (`gcloud` CLI):** Install and initialize the `gcloud` command-line tool on your machine.
    *   [Install Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
    *   Initialize it: `gcloud init`
3.  **Docker:** You already have this working!

## Deployment Steps:

### 1. Set your GCP Project:

Ensure your `gcloud` CLI is configured to the correct GCP project where you want to deploy.

```bash
gcloud config set project YOUR_GCP_PROJECT_ID
```

(Replace `YOUR_GCP_PROJECT_ID` with the project ID from your `.env` file or GCP console).

### 2. Enable Necessary APIs:

You need to enable the Cloud Run API and Artifact Registry API (or Container Registry API if you prefer the older service) in your GCP project.

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

### 3. Configure `ENV=production` in your `.env`:

For deployment, you'll want to use Google Cloud Storage. Change the `ENV` variable in your `.env` file to `production`. Also, ensure `GCP_PROJECT_ID` and `GCS_BUCKET_NAME` are correctly set to your actual GCP project ID and the name of the GCS bucket you want to use.

```env
ENV=production
GCP_PROJECT_ID="your-gcp-project-id"
GCS_BUCKET_NAME="your-gcs-bucket-name"
```

Make sure the `GCS_BUCKET_NAME` bucket actually exists in your GCP project. You can create it via the GCP Console or `gsutil mb gs://your-gcs-bucket-name`.

### 4. Set up API Keys in Google Secret Manager (Highly Recommended for Security):

Instead of putting your API keys directly in environment variables during deployment, it's best practice to store them securely in Google Secret Manager.

*   **Create secrets for your API keys:**

    ```bash
echo "YOUR_EXTRACTION_API_KEY" | gcloud secrets create EXTRACTION_API_KEY --data-file=-
    echo "YOUR_ANALYSIS_API_KEY" | gcloud secrets create ANALYSIS_API_KEY --data-file=-
    ```

    (Replace `YOUR_EXTRACTION_API_KEY` and `YOUR_ANALYSIS_API_KEY` with your actual keys).

*   **Grant Cloud Run service account access to these secrets:**

    Find your Cloud Run service account (usually `PROJECT_NUMBER-compute@developer.gserviceaccount.com` or `SERVICE_NAME@PROJECT_ID.iam.gserviceaccount.com`).

    ```bash
gcloud secrets add-iam-policy-binding EXTRACTION_API_KEY \
  --member="serviceAccount:YOUR_CLOUD_RUN_SERVICE_ACCOUNT_EMAIL" \
  --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding ANALYSIS_API_KEY \
  --member="serviceAccount:YOUR_CLOUD_RUN_SERVICE_ACCOUNT_EMAIL" \
  --role="roles/secretmanager.secretAccessor"
    ```

### 5. Build and Push Docker Image to Google Artifact Registry:

Google Cloud Run deploys images from Google's container registries. Artifact Registry is the recommended modern choice.

*   **Configure Docker to authenticate with Artifact Registry:**

    ```bash
gcloud auth configure-docker
    ```

*   **Tag your Docker image:** Replace `YOUR_REGION` (e.g., `us-central1`) and `YOUR_GCP_PROJECT_ID`.

    ```bash
docker tag bidder-analysis-app YOUR_REGION-docker.pkg.dev/YOUR_GCP_PROJECT_ID/bidder-analysis-repo/bidder-analysis-app:latest
    ```

*   **Push the image to Artifact Registry:**

    ```bash
docker push YOUR_REGION-docker.pkg.dev/YOUR_GCP_PROJECT_ID/bidder-analysis-repo/bidder-analysis-app:latest
    ```

### 6. Deploy to Cloud Run:

Now, deploy the image to Cloud Run. Replace `YOUR_REGION` and `YOUR_GCP_PROJECT_ID`.

```bash
gcloud run deploy bidder-analysis-app \
  --image YOUR_REGION-docker.pkg.dev/YOUR_GCP_PROJECT_ID/bidder-analysis-repo/bidder-analysis-app:latest \
  --platform managed \
  --region YOUR_REGION \
  --allow-unauthenticated \
  --set-env-vars ENV=production,GCP_PROJECT_ID=YOUR_GCP_PROJECT_ID,GCS_BUCKET_NAME=YOUR_GCS_BUCKET_NAME,EXTRACTION_LLM_PROVIDER=gemini,ANALYSIS_LLM_PROVIDER=gemini,EXTRACTION_MODEL_NAME=gemini-1.5-flash,ANALYSIS_MODEL_NAME=gemini-1.5-pro,EXTRACTION_TEMPERATURE=0.1,ANALYSIS_TEMPERATURE=0.2 \
  --set-secrets EXTRACTION_API_KEY=EXTRACTION_API_KEY:latest,ANALYSIS_API_KEY=ANALYSIS_API_KEY:latest
```

**Explanation of flags:**
*   `bidder-analysis-app`: The name of your Cloud Run service.
*   `--image`: Specifies the Docker image to deploy.
*   `--platform managed`: Uses the fully managed Cloud Run environment.
*   `--region`: Choose a GCP region close to your users (e.g., `us-central1`, `europe-west1`).
*   `--allow-unauthenticated`: Makes the service publicly accessible (useful for a web app). For production, you might want to restrict access.
*   `--set-env-vars`: Passes environment variables directly. **Important:** Do NOT put API keys here directly.
*   `--set-secrets`: This is crucial for API keys. It tells Cloud Run to pull the values from Google Secret Manager. You'll need to create these secrets first.

After successful deployment, `gcloud` will provide you with the URL of your deployed service.