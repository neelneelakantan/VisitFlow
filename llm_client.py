# llm_client.py

# llm_client.py
from google import genai
import os

def ask_gemini(prompt: str, model: str = "gemini-2.5-flash"):
    api_key = os.getenv("VISITFLOW_GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Gemini API key not found.")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text


