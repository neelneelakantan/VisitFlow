# llm_client.py
from google import genai
from google.genai import errors as genai_errors
import os

class LLMError(Exception):
    """Normalized error for UI consumption."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

def ask_gemini(prompt: str, model: str = "gemini-2.5-flash-lite"):
    api_key = os.getenv("VISITFLOW_GEMINI_API_KEY")
    if not api_key:
        raise LLMError("NO_API_KEY", "Gemini API key not found.")

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text

    except genai_errors.ServerError as e:
        # 503, 500, etc.
        if e.code == 503:
            raise LLMError(
                "MODEL_UNAVAILABLE",
                "Gemini is experiencing high demand. Try again shortly."
            )
        raise LLMError("SERVER_ERROR", str(e))

    except genai_errors.ClientError as e:
        # 400, invalid request, safety blocks, etc.
        raise LLMError("BAD_REQUEST", str(e))

    except Exception as e:
        # Catch-all fallback
        raise LLMError("UNKNOWN_ERROR", str(e))
