import json
import os
from . import config

# --- Provider Abstraction ---

def extract_data_from_text(text: str) -> dict:
    """
    Main function that routes to the correct LLM provider based on config.
    """
    provider = config.settings.LLM_PROVIDER.lower()
    
    if provider == "vertex":
        return _extract_with_vertex(text)
    # The openai implementation is kept for completeness, though not used in the new flow.
    elif provider == "openai":
        return _extract_with_openai(text)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

# --- Prompt Loading ---

def get_prompt(prompt_file: str) -> str:
    """Loads a prompt from the specified text file."""
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', prompt_file)
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

# --- Vertex AI (Gemini) Implementation ---

def _extract_with_vertex(text: str) -> dict:
    """Extracts data using Google's Vertex AI (Gemini)."""
    from vertexai.generative_models import GenerativeModel, GenerationConfig

    model = GenerativeModel(config.settings.VERTEX_MODEL_NAME)
    prompt = get_prompt("extraction_prompt.txt").format(text_content=text)
    
    generation_config = GenerationConfig(
        temperature=config.settings.TEMPERATURE,
        max_output_tokens=8192,
    )

    response = model.generate_content(prompt, generation_config=generation_config)
    
    try:
        json_str = response.text.strip().lstrip("```json").rstrip("```")
        return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error decoding JSON from Vertex AI response: {e}")
        print(f"Raw response: {response.text}")
        return {"fields": {}, "error": "Failed to parse LLM response"}

# --- OpenAI Implementation ---

def _extract_with_openai(text: str) -> dict:
    """Extracts data using OpenAI's API."""
    import openai

    client = openai.OpenAI(api_key=config.settings.OPENAI_API_KEY) # Note: OPENAI_API_KEY would need to be added to config
    prompt = get_prompt("extraction_prompt.txt").format(text_content=text)

    try:
        response = client.chat.completions.create(
            model=config.settings.OPENAI_MODEL_NAME, # Note: OPENAI_MODEL_NAME would need to be added to config
            messages=[
                {"role": "system", "content": "You are an expert assistant for analyzing procurement documents. Respond only with JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=config.settings.TEMPERATURE,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, openai.APIError) as e:
        print(f"Error calling or decoding JSON from OpenAI response: {e}")
        return {"fields": {}, "error": "Failed to call or parse LLM response"}
