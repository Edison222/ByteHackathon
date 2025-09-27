import os
from typing import Optional
from google import genai

_client: Optional[genai.Client] = None
DEFAULT_MODEL = "gemini-2.0-flash"  # or "gemini-2.5-flash" if available in your project

def _get_client() -> genai.Client:
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Set it in your environment or .env.")

    _client = genai.Client(api_key=api_key)
    return _client

def generate_response(prompt: str, system_instruction: str | None = None) -> str:
    client = _get_client()
    cfg = None
    if system_instruction:
        cfg = genai.types.GenerateContentConfig(system_instruction=system_instruction)

    resp = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config=cfg
    )
    return resp.text or ""

def embed_text(text: str):
    client = _get_client()
    resp = client.models.embed_content(
        model="models/embedding-001",
        contents=[{"parts":[{"text": text}]}]
    )
    return resp.embedding




