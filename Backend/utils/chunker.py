def chunk_text(text, chunk_size=150, overlap=30):
    if not text:
        return []

    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words)

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks

