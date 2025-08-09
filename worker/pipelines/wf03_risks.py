import json
from ..utils import gcs

def run(extraction_data: dict) -> dict:
    '''
    WF-03: Rules & Risks
    - Applies simple business rules to the extracted data.
    - Generates a list of risk flags.
    - Stores the result in GCS: `results/{case_id}/{doc_id}.risks.json`.
    - Returns the extraction data enriched with the risk analysis.
    '''
    case_id = extraction_data["case_id"]
    doc_id = extraction_data["doc_id"]
    fields = extraction_data.get("fields", {})
    
    print(f"  WF-03: Analyzing risks for doc_id: {doc_id}")
    
    flags = []

    # Rule 1: Check for missing payment terms
    if not fields.get("FormaPago") or "ambigu" in fields.get("FormaPago", "").lower():
        flags.append("PAGO_AMBIGUO")

    # Rule 2: Check for missing guarantees
    if not fields.get("GarantiaCumplimiento"):
        flags.append("FALTA_GARANTIA_CUMPLIMIENTO")

    # Rule 3: Check for penalties
    if fields.get("Penalidades"):
        flags.append("CONTIENE_PENALIDADES")
        
    # Rule 4: Stub for RUC validation
    if fields.get("ContratistaRUC"):
        # In a real scenario, this would call an external API.
        # For the demo, we just flag it for review.
        flags.append("TODO_VALIDAR_RUC")

    risk_analysis = {
        "doc_id": doc_id,
        "flags": flags,
        "diagnostics": extraction_data.get("diagnostics", {})
    }

    # Save the risk analysis to GCS
    result_path = f"results/{case_id}/{doc_id}.risks.json"
    gcs.upload_content(result_path, json.dumps(risk_analysis, indent=2), "application/json")
    
    print(f"  WF-03: Found {len(flags)} flags for {doc_id}. Saved to {result_path}")

    # Enrich the original extraction data and return it
    extraction_data["risk_analysis"] = risk_analysis
    return extraction_data
