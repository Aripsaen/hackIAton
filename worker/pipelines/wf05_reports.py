from ..utils import gcs, sheets, pdf as pdf_util, config
import datetime

def run(case_id: str, comparison_data: dict):
    """
    WF-05: Reports & Dashboard
    - Generates a minimal PDF summary report based on the new comparison data.
    - Appends/updates the Google Sheet with the new KPIs.
    """
    print(f"WF-05: Generating reports for case_id: {case_id}")

    # --- Generate PDF Report ---
    # This function now receives the new comparison_data structure
    report_path = f"reports/{case_id}/report.pdf"
    pdf_content = pdf_util.create_summary_pdf(comparison_data)
    gcs.upload_content(report_path, pdf_content, "application/pdf")
    report_url = f"gs://{config.settings.BUCKET_NAME}/{report_path}"
    print(f"  - PDF report saved to {report_url}")

    # --- Update Google Sheet ---
    rows_to_append = []
    timestamp = datetime.datetime.utcnow().isoformat()
    
    for bidder in comparison_data.get("bidders", []):
        kpis = bidder.get("kpis", {})
        # The analysis data is now nested inside the bidder object
        analysis = bidder.get("analysis", {})
        
        rows_to_append.append([
            timestamp,
            case_id,
            bidder.get("doc_id"),
            bidder.get("name"),
            kpis.get("cumplimiento"),
            kpis.get("riesgo"),
            kpis.get("monto"),
            analysis.get("categoria", "N/A"), # Add new category field
            analysis.get("totalPuntuacion", 0), # Add new total score
            report_url
        ])

    if rows_to_append:
        # Note: The append_to_sheet function might need its header row updated in Google Sheets manually
        sheets.append_to_sheet(rows_to_append)
        print(f"  - Appended {len(rows_to_append)} rows to Google Sheet.")