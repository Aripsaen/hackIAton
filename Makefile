.PHONY: install run-api build-api-docker push-api-docker build-worker-docker push-worker-docker

# Load environment variables from .env file
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# Default region if not set
REGION ?= us-central1

install:
	pip install -r api/requirements.txt
	pip install -r worker/requirements.txt

run-api:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Docker build and push for API
build-api-docker:
	docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/procurement/api:latest -f api/Dockerfile .

push-api-docker:
	docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/procurement/api:latest

# Docker build and push for Worker
build-worker-docker:
	docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/procurement/worker:latest -f worker/Dockerfile .

push-worker-docker:
	docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/procurement/worker:latest

help:
	@echo "Available commands:"
	@echo "  install                - Install Python dependencies for API and Worker"
	@echo "  run-api                - Run the FastAPI server locally"
	@echo "  build-api-docker       - Build the API Docker image"
	@echo "  push-api-docker        - Push the API Docker image to Artifact Registry"
	@echo "  build-worker-docker    - Build the Worker Docker image"
	@echo "  push-worker-docker     - Push the Worker Docker image to Artifact Registry"
