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

def run(case_id: str, comparison_data: dict, documents: list[dict]):
    """
    WF-05b: Final Case Analysis
    - Gathers all context (comparison data and all original texts).
    - Uses a powerful LLM (Gemini Pro) via LangChain to perform a final analysis.
    - Saves the final analysis to `results/{case_id}/final_analysis.json`.
    """
    print(f"  WF-05b: Starting final analysis for case_id: {case_id}")

    # 1. Initialize the powerful model
    analysis_model = ChatVertexAI(
        model_name=config.settings.VERTEX_PRO_MODEL_NAME,
        temperature=0.4, # Higher temperature for more nuanced analysis
        project=config.settings.PROJECT_ID,
    )

    # 2. Load the prompt
    analysis_prompt = get_prompt_template("analysis_prompt.txt")

    # 3. Define the chain
    analysis_chain = analysis_prompt | analysis_model | JsonOutputParser()

    # 4. Prepare the inputs
    # Concatenate all document texts to provide full context
    all_texts = "\n\n---\n\n".join([doc['text_content'] for doc in documents])
    
    input_data = {
        "comparison_data": json.dumps(comparison_data, indent=2),
        "all_texts": all_texts
    }

    # 5. Invoke the chain
    try:
        final_analysis = analysis_chain.invoke(input_data)
    except Exception as e:
        print(f"    - ERROR: LangChain analysis invocation failed: {e}")
        # Fail gracefully, create a placeholder artifact
        final_analysis = {
            "case_summary": {
                "error": "Failed to generate final analysis.",
                "details": str(e)
            }
        }

    # 6. Save the result
    analysis_path = f"results/{case_id}/final_analysis.json"
    gcs.upload_content(analysis_path, json.dumps(final_analysis, indent=2), "application/json")
    print(f"    - Saved final case analysis to {analysis_path}")

    return final_analysis
