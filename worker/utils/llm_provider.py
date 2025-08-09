import json
import os
from . import config

# --- Provider Abstraction ---

def extract_data_from_text(text: str) -> dict:
    '''
    Main function that routes to the correct LLM provider based on config.
    '''
    provider = config.settings.LLM_PROVIDER.lower()
    
    if provider == "vertex":
        return _extract_with_vertex(text)
    elif provider == "openai":
        return _extract_with_openai(text)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

# --- Prompt Loading ---

def get_prompt() -> str:
    '''Loads the extraction prompt from the text file.'''
    # This assumes the script is run from the repo root.
    # A more robust path would use __file__ to be location-independent.
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'extraction_prompt.txt')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

# --- Vertex AI (Gemini) Implementation ---

def _extract_with_vertex(text: str) -> dict:
    '''Extracts data using Google's Vertex AI (Gemini).'''
    from vertexai.generative_models import GenerativeModel, GenerationConfig

    model = GenerativeModel(config.settings.VERTEX_MODEL_NAME)
    prompt = get_prompt().format(text_content=text)
    
    generation_config = GenerationConfig(
        temperature=config.settings.TEMPERATURE,
        max_output_tokens=8192,
    )

    response = model.generate_content(prompt, generation_config=generation_config)
    
    try:
        # Clean the response to get only the JSON part
        json_str = response.text.strip().lstrip("```json").rstrip("```")
        return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error decoding JSON from Vertex AI response: {e}")
        print(f"Raw response: {response.text}")
        return {"fields": {}, "error": "Failed to parse LLM response"}

# --- OpenAI Implementation ---

def _extract_with_openai(text: str) -> dict:
    '''Extracts data using OpenAI's API.'''
    import openai

    client = openai.OpenAI(api_key=config.settings.OPENAI_API_KEY)
    prompt = get_prompt().format(text_content=text)

    try:
        response = client.chat.completions.create(
            model=config.settings.OPENAI_MODEL_NAME,
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
