# Shared helper for calling Gemini with retries (assignment step e)
import os
import json

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

genai.configure(api_key=os.environ["GEMINI_API_KEY"])


# Retries up to 3 times total, waiting 1s, then 2s, then 4s between attempts.
# If all 3 fail, re-raises the last error (caller decides how to handle it).
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10), reraise=True)
def call_gemini_json(prompt: str, model_name: str = "gemini-2.5-flash") -> dict:
    model = genai.GenerativeModel(
        model_name,
        generation_config={"response_mime_type": "application/json"},
    )
    response = model.generate_content(prompt)
    return json.loads(response.text)