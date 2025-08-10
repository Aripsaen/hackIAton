# Project Context: Automated Bidder Analysis Platform

This `GEMINI.md` file provides a concise overview of the project, its goals, and the technical decisions made during its development.

## Project Name

**Automated Bidder Analysis Platform**

## Overall Goal

The primary goal of this project is to create a web application that automates the analysis and comparison of bidder documents. It aims to streamline the process of ingesting PDF documents from multiple bidders, extracting key information, performing a rubric-based analysis using Large Language Models (LLMs), comparing the bidders, and generating a final comprehensive report.

## Key Functionalities (Workflows)

The application is structured around five core workflows:

*   **WF-01 – Ingest & Parsing**: Allows users to upload multiple PDF files, extracts raw text content, and stores both the original PDF and extracted text in a designated storage (GCS or local mock).
*   **WF-02 – Extraction (Per-Document)**: Uses a fast LLM (e.g., Gemini Flash) to extract detailed, structured JSON data from the text content of each document based on a predefined schema.
*   **WF-03 – Analysis (Per-Document)**: Uses a more capable LLM (e.g., Gemini Pro) via LangChain to evaluate the extracted JSON against a scoring rubric, generating scores and qualitative feedback for each document.
*   **WF-04 – Comparator**: Aggregates data from all extracted and analyzed documents for a given case, computes key performance indicators (KPIs), and generates a single, comprehensive comparison JSON object.
*   **WF-05 – Reporting**: Generates a human-readable PDF report summarizing all bidders, their scores, and KPIs based on the comparison data.

## Technology Stack

*   **Backend**: Python 3.11+, FastAPI
*   **Frontend**: Simple HTML, CSS, JavaScript (vanilla, no complex frameworks)
*   **LLM Orchestration**: LangChain (for vendor-agnostic LLM integration)
*   **LLM Models**: Configurable (Google Gemini Pro/Flash, OpenAI GPT models)
*   **PDF Parsing**: `pdfplumber`
*   **Report Generation**: `reportlab`
*   **Storage**: Google Cloud Storage (GCS) for deployment, with a local file-based mock for development.
*   **Deployment**: Docker (for easy containerization and deployment).

## Key Design Principles

*   **Modularity**: Code is organized into `core`, `services`, and `models` for clarity and maintainability.
*   **LLM Agnostic**: Designed to easily swap between different LLM providers (Gemini, OpenAI) by changing `.env` configuration, including independent API keys and temperature settings for extraction and analysis models.
*   **Development vs. Production**: Utilizes a mock storage client for local development to avoid cloud dependencies during testing, while seamlessly switching to GCS for production.
*   **Lightweight Frontend**: Prioritizes simplicity and speed with vanilla JS, HTML, and CSS.
*   **Containerization**: Aims for painless deployment via Docker.

## Current State / Progress

As of the last interaction, the core backend functionalities (WF-01 to WF-05) are implemented. The application is runnable locally via Python/pip or Docker. Recent efforts have focused on:

*   Refining the LLM configuration for independent API keys and temperature settings per model.
*   Implementing support for mixed LLM providers (e.g., Gemini for extraction, OpenAI for analysis).
*   Troubleshooting and fixing frontend-backend integration issues, particularly ensuring correct status updates and display of comparison results.
*   Providing extremely detailed setup instructions in `setup.md` for both local and Docker environments.

This project is ready for further testing, refinement, and potential expansion of its analysis capabilities.
