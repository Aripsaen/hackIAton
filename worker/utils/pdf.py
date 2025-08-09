import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from io import BytesIO

def extract_text_from_pdf(pdf_path: str) -> str:
    '''Extracts all text from a PDF file.'''
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def create_summary_pdf(comparison_data: dict) -> bytes:
    '''
    Generates a simple PDF report from the comparison data.
    '''
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(inch, height - inch, f"Reporte de Comparación - Caso: {comparison_data['case_id']}")

    # Summary
    p.setFont("Helvetica", 12)
    summary = comparison_data.get("summary", {})
    p.drawString(inch, height - 1.5 * inch, f"Mejor Oferta (doc_id): {summary.get('mejor_oferta_doc_id', 'N/A')}")

    # Table Header
    p.setFont("Helvetica-Bold", 10)
    y_pos = height - 2.5 * inch
    p.drawString(inch, y_pos, "Licitante (Contratista)")
    p.drawString(4 * inch, y_pos, "Cumplimiento")
    p.drawString(5.5 * inch, y_pos, "Riesgo")
    p.drawString(7 * inch, y_pos, "Monto")

    # Table Rows
    p.setFont("Helvetica", 9)
    y_pos -= 0.25 * inch
    for bidder in comparison_data.get("bidders", []):
        kpis = bidder.get("kpis", {})
        p.drawString(inch, y_pos, bidder.get("name", "N/A"))
        p.drawString(4 * inch, y_pos, str(kpis.get("cumplimiento", "0.0")))
        p.drawString(5.5 * inch, y_pos, str(kpis.get("riesgo", "0.0")))
        p.drawString(7 * inch, y_pos, f"{kpis.get('monto', 0):,.2f}")
        y_pos -= 0.25 * inch
        
        # Flags
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(inch + 0.2 * inch, y_pos, f"Flags: {', '.join(bidder.get('flags', []))}")
        y_pos -= 0.25 * inch
        p.setFont("Helvetica", 9)


    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer.getvalue()
