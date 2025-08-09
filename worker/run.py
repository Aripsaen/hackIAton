import argparse
from .utils import config, gcs
from .pipelines import (
    wf01_ingest,
    wf02_extract,
    wf03_analysis, # Formerly wf05_analysis
    wf04_compare,
    wf05_reports
)

def main(case_id: str):
    """
    Main function to run the entire document processing pipeline for a case.
    This pipeline has been re-orchestrated to support the new prompt structures.
    """
    print(f"--- Starting processing for case_id: {case_id} ---")
    
    job_id = f"job_for_{case_id}"
    gcs.update_job_status(config.settings.BUCKET_NAME, case_id, job_id, "running")

    try:
        # WF-01: Ingest and Parse PDFs from GCS. Returns a list of document dicts.
        print("--- Running WF-01: Ingest & Parsing ---")
        documents = wf01_ingest.run(case_id)
        if not documents:
            print(f"No documents found for case_id: {case_id}. Exiting.")
            gcs.update_job_status(config.settings.BUCKET_NAME, case_id, job_id, "done")
            return

        # WF-02: Extract structured data using the new, detailed prompt (LLM 1).
        print("--- Running WF-02: Structured Extraction ---")
        extractions = [wf02_extract.run(doc) for doc in documents]

        # WF-03: Perform rubric-based analysis on each extraction (LLM 2).
        print("--- Running WF-03: Rubric-based Analysis ---")
        analyses = [wf03_analysis.run(ext) for ext in extractions]

        # WF-04: Compare bidders based on both extraction and analysis data.
        print("--- Running WF-04: Comparison & KPI Calculation ---")
        # Pass both extractions and analyses to the comparison step
        comparison_result = wf04_compare.run(case_id, extractions, analyses)

        # WF-05: Generate PDF/Sheet reports based on the new comparison data.
        print("--- Running WF-05: Reporting ---")
        wf05_reports.run(case_id, comparison_result)
        
        print(f"--- Successfully finished processing for case_id: {case_id} ---")
        gcs.update_job_status(config.settings.BUCKET_NAME, case_id, job_id, "done")

    except Exception as e:
        print(f"!!! ERROR processing case_id: {case_id} - {e} !!!")
        gcs.update_job_status(config.settings.BUCKET_NAME, case_id, job_id, "error")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the procurement document analysis pipeline.")
    parser.add_argument("--case_id", type=str, required=True, help="The case_id to process.")
    args = parser.parse_args()
    
    main(args.case_id)
