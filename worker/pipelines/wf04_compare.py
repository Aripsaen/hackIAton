import json
from ..utils import gcs

def run(case_id: str, risk_analyses: list[dict]) -> dict:
    '''
    WF-04: Comparator
    - Aggregates multiple offers for the same case_id.
    - Computes KPIs (compliance, risk, amount).
    - Stores the result in GCS: `results/{case_id}/comparison.json`.
    - Returns the comparison data.
    '''
    print(f"WF-04: Comparing {len(risk_analyses)} documents for case_id: {case_id}")
    
    bidders = []
    for analysis in risk_analyses:
        doc_id = analysis["doc_id"]
        fields = analysis.get("fields", {})
        flags = analysis.get("risk_analysis", {}).get("flags", [])
        
        # KPI: Compliance score (0-1 scale)
        # Simple example: based on number of fields filled vs. expected
        expected_fields = ["EntidadContratante", "Contratista", "MontoTotal", "FormaPago", "GarantiaCumplimiento"]
        filled_fields = [f for f in expected_fields if fields.get(f)]
        compliance_kpi = len(filled_fields) / len(expected_fields)

        # KPI: Risk score (0-1 scale)
        # Simple example: based on number of risk flags
        risk_kpi = min(len(flags) / 3.0, 1.0) # Normalize based on ~3 major risks

        # KPI: Amount
        monto_str = str(fields.get("MontoTotal", "0")).replace(",", "")
        try:
            monto_kpi = float(monto_str)
        except (ValueError, TypeError):
            monto_kpi = 0.0

        bidders.append({
            "doc_id": doc_id,
            "name": fields.get("Contratista", "N/A"),
            "kpis": {
                "cumplimiento": round(compliance_kpi, 2),
                "riesgo": round(risk_kpi, 2),
                "monto": monto_kpi,
            },
            "flags": flags
        })

    # Determine the best offer (e.g., lowest amount with high compliance and low risk)
    mejor_oferta = sorted(
        bidders,
        key=lambda b: (b["kpis"]["riesgo"], b["kpis"]["monto"], -b["kpis"]["cumplimiento"])
    )
    
    comparison_result = {
        "case_id": case_id,
        "bidders": bidders,
        "summary": {
            "mejor_oferta_doc_id": mejor_oferta[0]["doc_id"] if mejor_oferta else None,
            "comentarios": "La mejor oferta se selecciona por menor riesgo, luego menor monto."
        }
    }

    # Save the comparison to GCS
    result_path = f"results/{case_id}/comparison.json"
    gcs.upload_content(result_path, json.dumps(comparison_result, indent=2), "application/json")
    
    print(f"WF-04: Saved comparison for {case_id} to {result_path}")
    
    return comparison_result
