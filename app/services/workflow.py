import os
import json
import uuid
import pdfplumber
from typing import List, Dict, Any
from datetime import datetime

from app.core.storage import storage_client
from app.core.llm import extraction_chain, analysis_chain, extraction_json_schema, analysis_json_schema
from app.models.schemas import ExtractionResult, AnalysisResult, ComparisonResult, BidderSummary
from app.services.ruc_lookup import fetch_ruc_info # Import the new service

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
        extracted_data_dict = await extract_data_with_llm(text_content)
        extracted_data = ExtractionResult(**extracted_data_dict)

        # New Step: RUC Lookup and Append (After WF-02, Before saving extraction.json)
        if extracted_data.partes.RUC:
            print(f"RUC found: {extracted_data.partes.RUC}. Attempting RUC lookup...")
            ruc_info = await fetch_ruc_info(extracted_data.partes.RUC)
            if ruc_info:
                extracted_data.ruc_info = ruc_info
                print(f"RUC info fetched and appended for {doc_id}.")
            else:
                print(f"Could not fetch RUC info for {extracted_data.partes.RUC}.")

        with open(extraction_json_path, "w", encoding="utf-8") as f:
            json.dump(extracted_data.model_dump(), f, indent=2, ensure_ascii=False)
        storage_client.upload_file(extraction_json_path, f"results/{case_id}/{doc_id}.extraction.json")
        print(f"Extraction complete for {doc_id}")

        # WF-03: Analysis (Per-Document)
        print(f"Starting analysis for {doc_id}...")
        analysis_data = await analyze_data_with_llm(extracted_data.model_dump())
        with open(analysis_json_path, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        storage_client.upload_file(analysis_json_path, f"results/{case_id}/{doc_id}.analysis.json")
        print(f"Analysis complete for {doc_id}")

        # Mark document as completed
        update_document_status(case_id, doc_id, "completed")

    except Exception as e:
        print(f"Error processing document {doc_id}: {e}")
        update_document_status(case_id, doc_id, "failed") # Mark as failed on error
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
            evaluacionRiesgos={
                "estadoRuc": {"puntuacion": 0, "comentario": "Error en análisis"},
                "requisitosLegales": {"puntuacion": 0, "comentario": "Error en análisis"},
                "viabilidadTecnica": {"puntuacion": 0, "comentario": "Error en análisis"},
                "viabilidadCronograma": {"puntuacion": 0, "comentario": "Error en análisis"},
                "garantiasPenalizaciones": {"puntuacion": 0, "comentario": "Error en análisis"}
            },
            kpis={
                "puntuacionTotal": 0,
                "ratioPuntuacionMonto": 0.0,
                "alineacionContratista": 0
            },
            resumenRiesgos={
                "puntosCriticos": ["Error en análisis"],
                "puntosDeMejora": ["Error en análisis"],
                "conclusion": "Análisis fallido."
            }
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

    # Compute KPIs (now directly from analysis result)
    kpis = {}
    for bidder in bidders:
        kpis[bidder.doc_id] = {
            "puntuacionTotal": bidder.analysis.kpis.puntuacionTotal,
            "ratioPuntuacionMonto": bidder.analysis.kpis.ratioPuntuacionMonto,
            "alineacionContratista": bidder.analysis.kpis.alineacionContratista
        }

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
    story.append(Paragraph(f"Informe de Análisis de Ofertas - ID de Caso: {case_id}", styles['h1']))
    story.append(Spacer(1, 0.2 * 100))

    # Summary Table
    summary_data = [["ID Oferente", "Contratista", "Monto Ofertado (USD)", "Puntuación Total", "Ratio Puntuación/Monto", "Alineación"]]
    for bidder in comparison_data.bidders:
        contractor_name = bidder.extraction.partes.Contratista or "N/A"
        monto_ofertado = bidder.extraction.oferta.montoOfertado.valor
        total_score = bidder.analysis.kpis.puntuacionTotal
        ratio_score_monto = bidder.analysis.kpis.ratioPuntuacionMonto
        alineacion = "Alineado" if bidder.analysis.kpis.alineacionContratista == 1 else "No Alineado"

        summary_data.append([
            bidder.doc_id,
            contractor_name,
            f"${monto_ofertado:,.2f}",
            str(total_score),
            f"{ratio_score_monto:.2f}",
            alineacion
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
        story.append(Paragraph(f"Análisis Detallado para el Oferente: {bidder.doc_id} ({bidder.extraction.partes.Contratista})", styles['h2']))
        story.append(Spacer(1, 0.1 * 100))

        story.append(Paragraph("**Resumen de Extracción:**", styles['h3']))
        story.append(Paragraph(f"Objeto del Contrato: {bidder.extraction.contrato.ObjetoContrato}", styles['Normal']))
        story.append(Paragraph(f"Monto Total: ${bidder.extraction.contrato.MontoTotal.valor:,.2f} {bidder.extraction.contrato.MontoTotal.moneda}", styles['Normal']))
        story.append(Paragraph(f"Forma de Pago: {bidder.extraction.contrato.FormaPago}", styles['Normal']))
        
        if bidder.extraction.ruc_info:
            story.append(Paragraph("**Información del RUC:**", styles['h3']))
            ruc_main = bidder.extraction.ruc_info.get("data", {}).get("main", [{}])[0]
            story.append(Paragraph(f"Razón Social: {ruc_main.get('razonSocial', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Estado Contribuyente: {ruc_main.get('estadoContribuyenteRuc', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Actividad Económica Principal: {ruc_main.get('actividadEconomicaPrincipal', 'N/A')}", styles['Normal']))
            # Add more RUC fields as needed

        story.append(Spacer(1, 0.1 * 100))

        story.append(Paragraph("**Evaluación de Riesgos (Puntuación):**", styles['h3']))
        risk_eval_data = [["Criterio", "Puntuación", "Comentario"]]
        for criterion, details in bidder.analysis.evaluacionRiesgos.model_dump().items():
            risk_eval_data.append([
                criterion.replace('_', ' ').title(),
                str(details['puntuacion']),
                details['comentario']
            ])
        risk_eval_table = Table(risk_eval_data, colWidths=[2*100, 0.8*100, 4*100])
        risk_eval_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(risk_eval_table)
        story.append(Spacer(1, 0.1 * 100))

        story.append(Paragraph("**KPIs Calculados:**", styles['h3']))
        story.append(Paragraph(f"Puntuación Total: {bidder.analysis.kpis.puntuacionTotal}", styles['Normal']))
        story.append(Paragraph(f"Ratio Puntuación/Monto: {bidder.analysis.kpis.ratioPuntuacionMonto:.2f}", styles['Normal']))
        story.append(Paragraph(f"Alineación del Contratista: {'Alineado' if bidder.analysis.kpis.alineacionContratista == 1 else 'No Alineado'}", styles['Normal']))
        story.append(Spacer(1, 0.1 * 100))

        story.append(Paragraph("**Resumen de Riesgos:**", styles['h3']))
        story.append(Paragraph(f"Puntos Críticos: {', '.join(bidder.analysis.resumenRiesgos.puntosCriticos)}", styles['Normal']))
        story.append(Paragraph(f"Puntos de Mejora: {', '.join(bidder.analysis.resumenRiesgos.puntosDeMejora)}", styles['Normal']))
        story.append(Paragraph(f"Conclusión: {bidder.analysis.resumenRiesgos.conclusion}", styles['Normal']))
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
    any_docs_failed = any(
        doc_info["status"] == "failed" 
        for doc_info in case_statuses[case_id]["documents"].values()
    )
    total_docs = len(case_statuses[case_id]["documents"])

    if total_docs == 0:
        case_statuses[case_id]["status"] = "empty"
    elif all_docs_completed:
        case_statuses[case_id]["status"] = "completed"
    elif any_docs_failed:
        case_statuses[case_id]["status"] = "partially_completed"
    else:
        case_statuses[case_id]["status"] = "processing"

def get_all_cases_summary() -> List[Dict[str, Any]]:
    summaries = []
    for case_id, case_info in case_statuses.items():
        summaries.append({
            "case_id": case_id,
            "document_count": len(case_info["documents"]),
            "status": case_info["status"]
        })
    return summaries
