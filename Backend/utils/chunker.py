def chunk_text(text, max_length=500):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]
