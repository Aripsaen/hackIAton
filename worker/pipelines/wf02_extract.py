import json
from ..utils import gcs, llm_provider, config, provenance

def run(document: dict) -> dict:
    """
    WF-02: Classification & Extraction
    - Loads the normalized text for a document.
    - Prompts the LLM to extract key fields into a normalized JSON structure.
    - Validates the LLM output and enriches it with provenance.
    - Stores the result in GCS: `results/{case_id}/{doc_id}.extraction.json`.
    - Returns the structured data.
    """
    case_id = document["case_id"]
    doc_id = document["doc_id"]
    text_content = document["text_content"]
    
    print(f"  WF-02: Extracting data for doc_id: {doc_id}")

    # Get the extraction result from the LLM provider
    structured_response = llm_provider.extract_data_from_text(text_content)

    # Basic validation and enrichment
    structured_response["doc_id"] = doc_id
    structured_response["schema_version"] = "v1"
    
    # The new prompt is responsible for provenance, so we remove the old client-side logic.
    structured_response["meta"]["doc_id"] = doc_id

    # Save the final JSON to GCS
    result_path = f"results/{case_id}/{doc_id}.extraction.json"
    gcs.upload_content(result_path, json.dumps(structured_response_with_provenance, indent=2), "application/json")
    
    print(f"  WF-02: Saved extraction for {doc_id} to {result_path}")
    
    # Return the data for the next pipeline step
    return structured_response_with_provenance
