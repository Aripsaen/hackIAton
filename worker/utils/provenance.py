import re

def find_evidence(field_value: str, text_content: str) -> tuple[str, int, int]:
    '''
    Finds the first occurrence of the field_value in the text content
    and returns the evidence snippet and character offsets.
    '''
    if not isinstance(field_value, str) or not field_value:
        return "", -1, -1

    # Use regex to find the value, ignoring case and allowing for minor whitespace differences
    try:
        # Escape special regex characters in the value
        escaped_value = re.escape(field_value)
        # Create a pattern that is more robust to whitespace
        pattern = re.sub(r'\s+', r'\s+', escaped_value)
        
        match = re.search(pattern, text_content, re.IGNORECASE)
        if match:
            start_char = match.start()
            end_char = match.end()
            # Create a snippet for context
            context_window = 30
            start_snippet = max(0, start_char - context_window)
            end_snippet = min(len(text_content), end_char + context_window)
            evidence = text_content[start_snippet:end_snippet]
            return evidence, start_char, end_char
    except re.error:
        # Fallback to simple string search if regex fails
        pass

    # Fallback to simple string search
    start_char = text_content.lower().find(field_value.lower())
    if start_char != -1:
        end_char = start_char + len(field_value)
        evidence = text_content[max(0, start_char-30):end_char+30]
        return evidence, start_char, end_char

    return "", -1, -1

def add_provenance_to_extraction(extraction_data: dict, text_content: str) -> dict:
    '''
    Iterates through extracted fields, finds their evidence in the source text,
    and adds a 'provenance' array to the data. Also identifies missing fields.
    '''
    provenance = []
    missing = []
    
    expected_fields = [
        "EntidadContratante", "Contratista", "ContratistaRUC", "ObjetoContrato",
        "financials", "Moneda", "PlazoEjecucion", "FechaDoc", "FormaPago",
        "GarantiaCumplimiento", "Penalidades"
    ]
    
    extracted_fields = extraction_data.get("fields", {})

    for field_name in expected_fields:
        field_value = extracted_fields.get(field_name)
        
        if field_value:
            evidence, start_char, end_char = find_evidence(str(field_value), text_content)
            if start_char != -1:
                provenance.append({
                    "field": field_name,
                    "evidence": evidence,
                    "start_char": start_char,
                    "end_char": end_char,
                })
        else:
            missing.append(field_name)

    extraction_data["provenance"] = provenance
    extraction_data["diagnostics"] = {"missing": missing}
    
    return extraction_data
