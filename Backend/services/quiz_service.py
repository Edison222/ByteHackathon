# services/quiz_service.py
import json, random, time
from typing import List, Dict, Any, Optional
from .gemini_service import generate_response
from .faiss_service import get_all_chunks, filter_chunks_by_sources
import re

# balanced across chosen files
def pick_quiz_chunks(course_id: str, sources: Optional[List[str]], num_questions: int, seed: Optional[int] = None) -> List[Dict[str, Any]]:
    rng = random.Random(seed or int(time.time()))
    entries = filter_chunks_by_sources(get_all_chunks(course_id), sources)

    if not entries:
        raise RuntimeError("No indexed chunks found for the requested sources. Upload/index the PDF(s) first.")


    # group by filename
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for e in entries:
        groups.setdefault(e.get("source","notes.pdf"), []).append(e)

    # shuffle within each group
    for v in groups.values():
        rng.shuffle(v)

    # round-robin sample so one file can't dominate
    picked: List[Dict[str, Any]] = []
    order = list(groups.keys())
    i = 0
    while len(picked) < num_questions and any(groups.values()):
        key = order[i % len(order)]
        if groups[key]:
            picked.append(groups[key].pop(0))
        i += 1

    return picked[:num_questions]

# MCQ generation
def _build_mcq_prompt(context_text: str, src_label: str) -> str:
    return f"""
Create EXACTLY ONE multiple-choice question (MCQ) based ONLY on the CONTEXT.

CONTEXT ({src_label})
{context_text}

RULES
- Question must be answerable solely from the context.
- Provide exactly 4 options (A–D) with ONE correct answer.
- Keep the question <= 25 words; each option <= 12 words.
- Return STRICT JSON ONLY (no prose, no markdown).
- In the explanation, explicitly reference the source like "({src_label})". Do NOT use [S#].

OUTPUT JSON SHAPE:
{{
  "type": "mcq",
  "question": "...",
  "options": ["...","...","...","..."],
  "correctIndex": 0,
  "explanation": "..."
}}
"""


def _json_call(prompt: str) -> Dict[str, Any]:
    """
    Call Gemini; enforce JSON output; try to parse; attempt recovery once.
    Raises RuntimeError with a helpful message if still non-JSON.
    """
    txt = generate_response(prompt, system_instruction="Return only valid JSON. No prose, no backticks.")
    if not txt or not txt.strip():
        # retry once
        txt = generate_response(
            prompt + "\nReturn ONLY JSON. No extra words.",
            system_instruction="Return only valid JSON. No prose, no backticks."
        )
        if not txt or not txt.strip():
            raise RuntimeError("LLM returned an empty response while generating quiz JSON.")

    # try direct parse
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        # try to salvage the largest JSON-looking block
        m = re.search(r'\{.*\}', txt, flags=re.S)
        if m:
            return json.loads(m.group(0))
        # last attempt: ask once more with an even stricter reminder
        txt2 = generate_response(
            "Return strictly valid JSON for the same request. No markdown, no prose. " + prompt,
            system_instruction="Return only valid JSON. No prose, no backticks."
        )
        try:
            return json.loads(txt2)
        except Exception:
            # give a concise error that helps debugging
            snippet = (txt2 or txt or "")[:300].replace("\n", " ")
            raise RuntimeError(f"LLM returned non-JSON: {snippet}")

def make_mcq_from_chunk(chunk: Dict[str, Any], s_tag: str) -> Dict[str, Any]:
    ctx = (chunk.get("text") or "").replace("\n"," ").strip()
    if len(ctx) > 1200:
        ctx = ctx[:1200] + "…"

    # build a readable label like "Lecture_14.pdf" or "Lecture_14.pdf, p. 12"
    src = chunk.get("source") or "notes.pdf"
    page = chunk.get("page")
    src_label = f"{src}, p. {page}" if page else src

    try:
        obj = _json_call(_build_mcq_prompt(ctx, src_label))
    except Exception:
        base = ctx[:180] or "According to the notes"
        obj = {
            "type": "mcq",
            "question": f"What best matches the statement in ({src_label})?",
            "options": [
                base,
                base.replace(" the ", " a "),
                "A partially correct paraphrase of the statement",
                "An unrelated option"
            ],
            "correctIndex": 0,
            "explanation": f"The exact phrasing appears in ({src_label})."
        }

    # attach citation for UI
    obj["citation"] = {"tag": s_tag, "source": src, "page": page}
    obj["id"] = obj.get("id")  # keep as-is; set in caller
    return obj



def generate_mcq_quiz(course_id: str,
                      sources: Optional[List[str]],
                      num_questions: int = 6,
                      seed: Optional[int] = None) -> Dict[str, Any]:
    chunks = pick_quiz_chunks(course_id, sources, num_questions, seed=seed)
    questions = []
    for i, ch in enumerate(chunks, start=1):
        tag = f"S{i}"
        q = make_mcq_from_chunk(ch, tag)
        q["id"] = f"Q{i}"
        questions.append(q)
    return {
        "courseId": course_id,
        "sourcesUsed": sorted({c.get("source") for c in chunks if c.get("source")}),
        "questions": questions
    }
