import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_rag_answer(question, context):
    if not context.strip():
        return "I could not find relevant course material to answer that question."

    prompt = f"""
You are a helpful study assistant.

Use only the provided context to answer the student's question.
If the answer is not in the context, say that the information is not available in the provided material.

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a helpful and accurate tutoring assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content