import os
import json
import re
import httpx
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

async def generate_completion(messages: List[Dict[str, str]], max_tokens: int = 500, temperature: float = 0.6) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")

    payload = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "n": 1
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(OPENAI_URL, json=payload, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

def extract_json(text: str):
    """
    Try to extract JSON object or array from arbitrary model output.
    Returns Python object or None.
    """
    # naive attempt: find first { or [ and last matching } or ]
    text = text.strip()
    # remove leading commentary lines
    # find first occurrence of { or [
    match = re.search(r"(\{|\[)", text)
    if not match:
        return None
    start = match.start()
    candidate = text[start:]
    # Attempt incremental parse: try full candidate, then try trimming trailing characters
    for i in range(len(candidate), 0, -1):
        try:
            obj = json.loads(candidate[:i])
            return obj
        except Exception:
            continue
    # last resort: try to find matching brackets using stack for {} or []
    # fallback: None
    return None
