from typing import List

def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    """Word-based chunking with overlap, robust and simple."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+chunk_size]
        if not chunk:
            break
        chunks.append(" ".join(chunk))
        i += max(1, chunk_size - overlap)
    return chunks

