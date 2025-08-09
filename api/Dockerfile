# Use the official Python image.
FROM python:3.11-slim

# Set the working directory.
WORKDIR /app

# Copy local code to the container image.
COPY ./api /app/api
COPY ./worker/prompts /app/worker/prompts

# Install production dependencies.
COPY ./api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Set the entrypoint command
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
