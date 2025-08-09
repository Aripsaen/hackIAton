# Placeholder for future text chunking logic.
# For Phase 1, we assume the entire document text can be sent to the LLM
# in a single prompt, as documents are expected to be relatively small.
# A more robust implementation would split large texts into deterministic
# chunks to fit within the LLM's context window.

def chunk_text(text: str, chunk_size: int = 4000, chunk_overlap: int = 200) -> list[str]:
    '''
    A simple chunking strategy. Not used in Phase 1.
    '''
    # This is a naive implementation. A better one would respect sentence boundaries.
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - chunk_overlap)]
