import re

def normalize_text(text: str) -> str:
    '''
    Normalizes text by removing excessive whitespace and standardizing line breaks.
    This creates a "flattened" version of the text for reliable character offsets.
    '''
    # Replace multiple newlines/spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def filename_to_doc_id(filename: str) -> str:
    '''
    Creates a stable, filesystem-friendly ID from a filename.
    Example: "Oferta Económica v2 (final).pdf" -> "oferta-economica-v2-final"
    '''
    # Remove extension
    base = filename.rsplit('.', 1)[0]
    # Convert to lowercase and replace non-alphanumeric chars with a hyphen
    base = re.sub(r'[^a-z0-9]+', '-', base.lower()).strip('-')
    return base
