import json
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from ..utils import gcs, config

def get_prompt_template(filename: str) -> ChatPromptTemplate:
    """Loads a prompt from the specified file."""
    import os
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', filename)
    return ChatPromptTemplate.from_template(open(prompt_path, 'r', encoding='utf-8').read())

def run(extraction_data: dict):
    """
    WF-03: Rubric-based Analysis
    - Takes the structured JSON from the extraction step.
    - Uses Gemini Pro to perform a detailed analysis based on the rubric.
    - Saves the analysis to `results/{case_id}/{doc_id}.analysis.json`.
    """
    case_id = extraction_data["meta"]["doc_id"]
    doc_id = case_id # In this new flow, we assume doc_id is the case_id for simplicity
    
    print(f"  WF-03: Starting rubric-based analysis for doc_id: {doc_id}")

    analysis_model = ChatVertexAI(
        model_name=config.settings.VERTEX_PRO_MODEL_NAME,
        temperature=0.2, # Low temperature for consistent rubric scoring
        project=config.settings.PROJECT_ID,
    )

    analysis_prompt = get_prompt_template("analysis_prompt.txt")
    analysis_chain = analysis_prompt | analysis_model | JsonOutputParser()

    try:
        # The new prompt expects the JSON data directly
        analysis_result = analysis_chain.invoke(extraction_data)
    except Exception as e:
        print(f"    - ERROR: LangChain analysis invocation failed: {e}")
        analysis_result = {"error": "Failed to generate analysis.", "details": str(e)}

    analysis_path = f"results/{case_id}/{doc_id}.analysis.json"
    gcs.upload_content(analysis_path, json.dumps(analysis_result, indent=2), "application/json")
    print(f"    - Saved rubric analysis to {analysis_path}")

    return analysis_result