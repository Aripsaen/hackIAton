# Use the official Python image.
FROM python:3.11-slim

# Set the working directory.
WORKDIR /app

# Install system dependencies that might be needed by libraries like PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends     libgl1-mesa-glx     && rm -rf /var/lib/apt/lists/*

# Copy local code to the container image.
COPY ./worker /app/worker

# Install production dependencies.
COPY ./worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Set the entrypoint command to run the worker script.
# The --case_id will be passed as an argument during the Cloud Run Job execution.
ENTRYPOINT ["python", "-m", "worker.run"]

