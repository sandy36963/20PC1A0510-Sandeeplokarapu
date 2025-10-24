import json
import requests
from typing import List, Dict


def llm_summarize(events: List[Dict], ocr_snippets: List[Dict], audio_snippets: List[Dict], model: str = "llama3.2:3b") -> str:
    prompt = f"""
You are an assistant that explains a user's recent computer activity.
Events (JSON lines) and texts are below. Summarize in 3-8 sentences.
Also list any repetitive action candidates as bullet points.

EVENTS (truncated):
{json.dumps(events[-200:], indent=2)}

OCR TEXT (truncated):
{"\n".join([o.get("text", "")[:500] for o in ocr_snippets[-10:]])}

AUDIO TEXT (truncated):
{"\n".join([a.get("text", "")[:500] for a in audio_snippets[-10:]])}
"""
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json().get("response", "")
