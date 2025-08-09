import argparse
import os
from .utils import config, gcs
from .pipelines import wf01_ingest, wf02_extract, wf03_risks, wf04_compare, wf05_reports

def main(case_id: str):
    '''
    Main function to run the entire document processing pipeline for a case.
    '''
    print(f"--- Starting processing for case_id: {case_id} ---")
    
    # Simplified job status tracking using GCS markers
    job_id = f"job_for_{case_id}" # Must match API's placeholder logic
    gcs.update_job_status(config.settings.BUCKET_NAME, case_id, job_id, "running")

    try:
        # WF-01: Ingest and Parse PDFs from GCS
        print("--- Running WF-01: Ingest & Parsing ---")
        documents = wf01_ingest.run(case_id)
        if not documents:
            print(f"No documents found for case_id: {case_id}. Exiting.")
            gcs.update_job_status(config.settings.BUCKET_NAME, case_id, job_id, "done")
            return

        # WF-02: Extract structured data using LLM
        print("--- Running WF-02: Extraction ---")
        extractions = [wf02_extract.run(doc) for doc in documents]

        # WF-03: Apply business rules and identify risks
        print("--- Running WF-03: Risk Analysis ---")
        risk_analyses = [wf03_risks.run(ext) for ext in extractions]

        # WF-04: Compare bidders and calculate KPIs
        print("--- Running WF-04: Comparison ---")
        comparison_result = wf04_compare.run(case_id, risk_analyses)

        # WF-05: Generate reports and update dashboard
        print("--- Running WF-05: Reporting ---")
        wf05_reports.run(case_id, comparison_result)

        print(f"--- Successfully finished processing for case_id: {case_id} ---")
        gcs.update_job_status(config.settings.BUCKET_NAME, case_id, job_id, "done")

    except Exception as e:
        print(f"!!! ERROR processing case_id: {case_id} - {e} !!!")
        gcs.update_job_status(config.settings.BUCKET_NAME, case_id, job_id, "error")
        # Re-raise the exception to make the Cloud Run Job fail explicitly
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the procurement document analysis pipeline.")
    parser.add_argument("--case_id", type=str, required=True, help="The case_id to process.")
    args = parser.parse_args()
    
    main(args.case_id)
