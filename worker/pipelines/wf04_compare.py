import json
from ..utils import gcs

def run(case_id: str, extractions: list[dict], analyses: list[dict]) -> dict:
    """
    WF-04: Comparator
    - Aggregates data from both extractions and analyses.
    - Computes KPIs based on the new, detailed data structures.
    - Stores the result in `results/{case_id}/comparison.json`.
    """
    print(f"WF-04: Comparing {len(extractions)} documents for case_id: {case_id}")
    
    bidders = []
    for i, extraction in enumerate(extractions):
        analysis = analyses[i] # Assumes a 1-to-1 correspondence
        doc_id = extraction.get("meta", {}).get("doc_id", f"doc_{i}")
        
        # KPI: Monto (Amount)
        monto_kpi = extraction.get("oferta", {}).get("montoOfertado", {}).get("valor", 0)

        # KPI: Cumplimiento (Compliance Score)
        # Derived from the rubric score in the analysis output
        total_puntuacion = analysis.get("totalPuntuacion", 0)
        # Normalize from 50 (10 criteria * 5) to a 0-1 scale
        compliance_kpi = total_puntuacion / 50.0 

        # KPI: Riesgo (Risk Score)
        # Derived from the category in the analysis output
        categoria_riesgo = analysis.get("categoria", "Riesgo Alto").lower()
        risk_map = {"riesgo bajo": 0.2, "riesgo medio": 0.5, "riesgo alto": 0.8}
        risk_kpi = risk_map.get(categoria_riesgo, 0.8)

        bidders.append({
            "doc_id": doc_id,
            "name": extraction.get("partes", {}).get("Contratista", "N/A"),
            "kpis": {
                "cumplimiento": round(compliance_kpi, 2),
                "riesgo": round(risk_kpi, 2),
                "monto": monto_kpi,
            },
            # Pass the full analysis for this bidder to the frontend
            "analysis": analysis 
        })

    mejor_oferta = sorted(
        bidders,
        key=lambda b: (b["kpis"]["riesgo"], b["kpis"]["monto"], -b["kpis"]["cumplimiento"])
    )
    
    comparison_result = {
        "case_id": case_id,
        "bidders": bidders,
        "summary": {
            "mejor_oferta_doc_id": mejor_oferta[0]["doc_id"] if mejor_oferta else None,
            "comentarios": "La mejor oferta se selecciona por menor riesgo, luego menor monto y mayor cumplimiento."
        }
    }

    result_path = f"results/{case_id}/comparison.json"
    gcs.upload_content(result_path, json.dumps(comparison_result, indent=2), "application/json")
    print(f"WF-04: Saved new comparison for {case_id} to {result_path}")
    
    return comparison_result