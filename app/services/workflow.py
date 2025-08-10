import os
import json
import uuid
import pdfplumber
from typing import List, Dict, Any
from datetime import datetime

from app.core.storage import storage_client
from app.core.llm import extraction_chain, analysis_chain, extraction_json_schema, analysis_json_schema
from app.models.schemas import ExtractionResult, AnalysisResult, ComparisonResult, BidderSummary

# Temporary directory for processing files
TEMP_DIR = "./temp"
os.makedirs(TEMP_DIR, exist_ok=True)

async def process_document_workflow(
    case_id: str,
    doc_id: str,
    file_content: bytes,
    file_name: str
):
    """Orchestrates the entire document processing workflow for a single document."""
    print(f"Starting workflow for case_id: {case_id}, doc_id: {doc_id}, file_name: {file_name}")

    pdf_path = os.path.join(TEMP_DIR, f"{doc_id}.pdf")
    text_path = os.path.join(TEMP_DIR, f"{doc_id}.txt")
    extraction_json_path = os.path.join(TEMP_DIR, f"{doc_id}.extraction.json")
    analysis_json_path = os.path.join(TEMP_DIR, f"{doc_id}.analysis.json")

    try:
        # WF-01: Ingest & Parsing
        with open(pdf_path, "wb") as f:
            f.write(file_content)
        print(f"Saved PDF to {pdf_path}")

        text_content = extract_text_from_pdf(pdf_path)
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        print(f"Extracted text to {text_path}")

        # Store original PDF and extracted text in GCS (or mock)
        storage_client.upload_file(pdf_path, f"{case_id}/{doc_id}.pdf")
        storage_client.upload_file(text_path, f"{case_id}/{doc_id}.txt")

        # WF-02: Extraction (Per-Document)
        print(f"Starting extraction for {doc_id}...")
        extracted_data = await extract_data_with_llm(text_content)
        with open(extraction_json_path, "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        storage_client.upload_file(extraction_json_path, f"results/{case_id}/{doc_id}.extraction.json")
        print(f"Extraction complete for {doc_id}")

        # WF-03: Analysis (Per-Document)
        print(f"Starting analysis for {doc_id}...")
        analysis_data = await analyze_data_with_llm(extracted_data)
        with open(analysis_json_path, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        storage_client.upload_file(analysis_json_path, f"results/{case_id}/{doc_id}.analysis.json")
        print(f"Analysis complete for {doc_id}")

    except Exception as e:
        print(f"Error processing document {doc_id}: {e}")
    finally:
        # Clean up temporary files
        for f_path in [pdf_path, text_path, extraction_json_path, analysis_json_path]:
            if os.path.exists(f_path):
                os.remove(f_path)
        print(f"Cleaned up temporary files for {doc_id}")

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text content from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        raise
    return text

async def extract_data_with_llm(text_content: str) -> Dict[str, Any]:
    """Uses LLM to extract structured data from text content."""
    try:
        # LangChain expects the schema as a string for the prompt
        response = await extraction_chain.ainvoke({
            "json_schema": json.dumps(extraction_json_schema, ensure_ascii=False),
            "text": text_content
        })
        # The response from Gemini is often a string that needs to be parsed as JSON
        # It might be wrapped in markdown code block, so we need to handle that.
        json_string = response.content.strip()
        if json_string.startswith("```json") and json_string.endswith("```"):
            json_string = json_string[7:-3].strip()
        return json.loads(json_string)
    except Exception as e:
        print(f"Error during LLM extraction: {e}")
        # Return a default empty structure if extraction fails
        return ExtractionResult().model_dump()

async def analyze_data_with_llm(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """Uses LLM to analyze extracted data based on a rubric."""
    try:
        response = await analysis_chain.ainvoke({
            "json_schema": json.dumps(analysis_json_schema, ensure_ascii=False),
            "json_data": json.dumps(extracted_data, indent=2, ensure_ascii=False)
        })
        json_string = response.content.strip()
        if json_string.startswith("```json") and json_string.endswith("```"):
            json_string = json_string[7:-3].strip()
        return json.loads(json_string)
    except Exception as e:
        print(f"Error during LLM analysis: {e}")
        # Return a default empty structure if analysis fails
        return AnalysisResult(
            calificacion={
                "cumplimientoRequisitosLegales": {"puntuacion": 0, "comentario": "Error en análisis"},
                "claridadYComplejidadTecnica": {"puntuacion": 0, "comentario": "Error en análisis"},
                "viabilidadDelCronogramaDeEjecucion": {"puntuacion": 0, "comentario": "Error en análisis"},
                "evaluacionDeRiesgosFinancierosYEconomicos": {"puntuacion": 0, "comentario": "Error en análisis"},
                "garantiasYPenalizaciones": {"puntuacion": 0, "comentario": "Error en análisis"},
                "condicionesDePagoYAvances": {"puntuacion": 0, "comentario": "Error en análisis"},
                "capacidadesTecnicasDelContratista": {"puntuacion": 0, "comentario": "Error en análisis"},
                "mecanismosDeResolucionDeConflictos": {"puntuacion": 0, "comentario": "Error en análisis"},
                "cumplimientoConNormativasTecnicasYLegales": {"puntuacion": 0, "comentario": "Error en análisis"},
                "impactoYSostenibilidadDelProyecto": {"puntuacion": 0, "comentario": "Error en análisis"}
            },
            totalPuntuacion=0,
            categoria="Error",
            analisis={"puntosFuertes": [], "puntosDeMejora": []},
            conclusion="Análisis fallido."
        ).model_dump()

async def get_comparison_report(case_id: str) -> ComparisonResult:
    """WF-04: Aggregates extraction and analysis results for comparison."""
    print(f"Generating comparison report for case_id: {case_id}")
    # List all extraction and analysis files for the given case_id
    extraction_files = storage_client.list_files(f"results/{case_id}/")
    
    bidders: List[BidderSummary] = []
    
    for file_path in extraction_files:
        if file_path.endswith(".extraction.json"):
            doc_id = file_path.split('/')[-1].replace('.extraction.json', '')
            
            temp_extraction_path = os.path.join(TEMP_DIR, f"{doc_id}.extraction.json")
            temp_analysis_path = os.path.join(TEMP_DIR, f"{doc_id}.analysis.json")
            
            try:
                storage_client.download_file(file_path, temp_extraction_path)
                storage_client.download_file(f"results/{case_id}/{doc_id}.analysis.json", temp_analysis_path)
                
                with open(temp_extraction_path, "r", encoding="utf-8") as f:
                    extraction_data = json.load(f)
                with open(temp_analysis_path, "r", encoding="utf-8") as f:
                    analysis_data = json.load(f)
                
                # Assuming file_name can be derived or stored somewhere
                # For now, let's use doc_id as a placeholder for file_name
                file_name = f"{doc_id}.pdf" 

                bidders.append(BidderSummary(
                    doc_id=doc_id,
                    file_name=file_name,
                    extraction=ExtractionResult(**extraction_data),
                    analysis=AnalysisResult(**analysis_data)
                ))
            except Exception as e:
                print(f"Could not load data for doc_id {doc_id}: {e}")
            finally:
                if os.path.exists(temp_extraction_path): os.remove(temp_extraction_path)
                if os.path.exists(temp_analysis_path): os.remove(temp_analysis_path)

    # Compute KPIs (example: score_per_dollar_offered)
    kpis = {}
    for bidder in bidders:
        monto_ofertado = bidder.extraction.oferta.montoOfertado.valor
        total_puntuacion = bidder.analysis.totalPuntuacion
        if monto_ofertado > 0:
            kpis[bidder.doc_id] = {"score_per_dollar_offered": total_puntuacion / monto_ofertado}
        else:
            kpis[bidder.doc_id] = {"score_per_dollar_offered": 0}

    comparison_result = ComparisonResult(
        case_id=case_id,
        bidders=bidders,
        kpis=kpis
    )
    
    # Save the comparison.json
    comparison_json_path = os.path.join(TEMP_DIR, f"{case_id}.comparison.json")
    with open(comparison_json_path, "w", encoding="utf-8") as f:
        json.dump(comparison_result.model_dump(), f, indent=2, ensure_ascii=False)
    storage_client.upload_file(comparison_json_path, f"results/{case_id}/comparison.json")
    os.remove(comparison_json_path)

    return comparison_result


async def generate_report_pdf(case_id: str) -> str:
    """WF-05: Generates a human-readable PDF report from comparison data."""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    print(f"Generating PDF report for case_id: {case_id}")

    comparison_data: ComparisonResult = await get_comparison_report(case_id)
    report_path = os.path.join(TEMP_DIR, f"{case_id}_report.pdf")

    doc = SimpleDocTemplate(report_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(f"Bidder Analysis Report - Case ID: {case_id}", styles['h1']))
    story.append(Spacer(1, 0.2 * 100))

    # Summary Table
    summary_data = [["Bidder ID", "Contractor", "Offered Amount (USD)", "Total Score", "Score/Dollar"]] # Added Score/Dollar
    for bidder in comparison_data.bidders:
        contractor_name = bidder.extraction.partes.Contratista or "N/A"
        monto_ofertado = bidder.extraction.oferta.montoOfertado.valor
        total_puntuacion = bidder.analysis.totalPuntuacion
        score_per_dollar = comparison_data.kpis.get(bidder.doc_id, {}).get("score_per_dollar_offered", 0)
        summary_data.append([
            bidder.doc_id,
            contractor_name,
            f"${monto_ofertado:,.2f}",
            str(total_puntuacion),
            f"{score_per_dollar:.4f}"
        ])
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.4 * 100))

    # Detailed Analysis for each bidder
    for bidder in comparison_data.bidders:
        story.append(Paragraph(f"Detailed Analysis for Bidder: {bidder.doc_id} ({bidder.extraction.partes.Contratista})", styles['h2']))
        story.append(Spacer(1, 0.1 * 100))

        story.append(Paragraph("**Extraction Summary:**", styles['h3']))
        story.append(Paragraph(f"Object of Contract: {bidder.extraction.contrato.ObjetoContrato}", styles['Normal']))
        story.append(Paragraph(f"Total Amount: ${bidder.extraction.contrato.MontoTotal.valor:,.2f} {bidder.extraction.contrato.MontoTotal.moneda}", styles['Normal']))
        story.append(Paragraph(f"Payment Form: {bidder.extraction.contrato.FormaPago}", styles['Normal']))
        story.append(Spacer(1, 0.1 * 100))

        story.append(Paragraph("**Analysis Scores:**", styles['h3']))
        analysis_scores_data = [["Criterion", "Score", "Comment"]]
        for criterion, details in bidder.analysis.calificacion.model_dump().items():
            analysis_scores_data.append([
                criterion.replace('_', ' ').title(),
                str(details['puntuacion']),
                details['comentario']
            ])
        analysis_scores_table = Table(analysis_scores_data, colWidths=[2*100, 0.8*100, 4*100])
        analysis_scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(analysis_scores_table)
        story.append(Spacer(1, 0.1 * 100))

        story.append(Paragraph("**Overall Analysis:**", styles['h3']))
        story.append(Paragraph(f"Strong Points: {', '.join(bidder.analysis.analisis.puntosFuertes)}", styles['Normal']))
        story.append(Paragraph(f"Improvement Points: {', '.join(bidder.analysis.analisis.puntosDeMejora)}", styles['Normal']))
        story.append(Paragraph(f"Conclusion: {bidder.analysis.conclusion}", styles['Normal']))
        story.append(Spacer(1, 0.4 * 100))

    doc.build(story)
    print(f"PDF report generated at {report_path}")
    return report_path


# In-memory store for case status (for simplicity in hackathon project)
# In a real app, this would be a database
case_statuses: Dict[str, Dict[str, Any]] = {}

def get_case_status(case_id: str) -> Dict[str, Any]:
    return case_statuses.get(case_id, {"status": "not_found", "documents": {}})

def update_document_status(case_id: str, doc_id: str, status: str, file_name: str = ""):
    if case_id not in case_statuses:
        case_statuses[case_id] = {"status": "processing", "documents": {}}
    case_statuses[case_id]["documents"][doc_id] = {"status": status, "file_name": file_name}
    
    # Update overall case status based on document statuses
    all_docs_completed = all(
        doc_info["status"] == "completed" 
        for doc_info in case_statuses[case_id]["documents"].values()
    )
    if all_docs_completed and case_statuses[case_id]["documents"]:
        case_statuses[case_id]["status"] = "completed"
    elif not all_docs_completed and case_statuses[case_id]["documents"]:
        case_statuses[case_id]["status"] = "processing"
    else:
        case_statuses[case_id]["status"] = "empty"

def get_all_cases_summary() -> List[Dict[str, Any]]:
    summaries = []
    for case_id, case_info in case_statuses.items():
        summaries.append({
            "case_id": case_id,
            "document_count": len(case_info["documents"]),
            "status": case_info["status"]
        })
    return summaries
