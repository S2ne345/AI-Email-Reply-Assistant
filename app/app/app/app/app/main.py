import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import asyncio
import json

from .openai_client import generate_completion, extract_json
from .prompt_templates import build_messages
from .email_sender import send_email

load_dotenv()

app = FastAPI(title="AI Email Reply Assistant (Prototype)")

class EmailInput(BaseModel):
    subject: Optional[str]
    from_: EmailStr
    to: Optional[str]
    body: str

    class Config:
        fields = {"from_": "from"}

class ThreadItem(BaseModel):
    from_: Optional[str]
    body: str
    date: Optional[str]

    class Config:
        fields = {"from_": "from"}

class GenerateRequest(BaseModel):
    email: EmailInput
    tones: Optional[List[str]] = ["formal", "friendly"]
    maxDrafts: Optional[int] = 2
    thread_history: Optional[List[ThreadItem]] = []

class SendRequest(BaseModel):
    to: EmailStr
    subject: Optional[str] = None
    body: str
    fromName: Optional[str] = None

@app.get("/")
async def health():
    return {"status": "AI Email Reply Assistant running"}

@app.post("/generate-drafts")
async def generate_drafts(req: GenerateRequest):
    email = {
        "subject": req.email.subject,
        "from": req.email.from_,
        "to": req.email.to,
        "body": req.email.body
    }
    thread = []
    for item in req.thread_history:
        thread.append({"from": item.from_, "body": item.body, "date": item.date})

    drafts = []
    try:
        # Limit drafts to available tones and maxDrafts
        count = min(len(req.tones), req.maxDrafts)
        for i in range(count):
            tone = req.tones[i]
            messages = build_messages(email, thread, tone)
            content = await generate_completion(messages, max_tokens=500, temperature=0.6)
            parsed = extract_json(content)
            if parsed is None:
                # fallback: wrap plain text
                parsed = {
                    "label": f"draft_{i+1}",
                    "tone": tone,
                    "draft": content.strip(),
                    "suggested_action_items": []
                }
            drafts.append(parsed)
        return {"drafts": drafts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send")
async def send(req: SendRequest):
    try:
        await send_email(to_email=req.to, subject=req.subject or "(no subject)", body_text=req.body, from_name=req.fromName)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=False)
