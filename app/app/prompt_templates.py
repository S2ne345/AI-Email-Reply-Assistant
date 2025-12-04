from typing import List, Dict

SYSTEM_PROMPT = (
    "You are an assistant that drafts concise, professional email replies. "
    "Produce 1 reply draft in the requested tone. Each draft should be 2–6 sentences unless otherwise requested. "
    "Also include up to 3 suggested action items."
)

def build_messages(email: Dict[str, str], thread_history: List[Dict[str, str]], tone: str, instructions: str = ""):
    """
    email: {subject, from, to, body}
    thread_history: list of {from, body, date} (optional)
    tone: label like 'formal', 'friendly', 'concise'
    """
    history_text = ""
    if thread_history:
        parts = []
        for idx, m in enumerate(thread_history, 1):
            parts.append(f"{idx}. From: {m.get('from','unknown')} | Date: {m.get('date','unknown')}\n   {m.get('body','')}")
        history_text = "Conversation history:\n" + "\n".join(parts) + "\n\n"

    user_content = (
        f"Input email:\nSubject: {email.get('subject','(no subject)')}\nFrom: {email.get('from')}\nTo: {email.get('to','(me)')}\n\n"
        f"Body:\n{email.get('body')}\n\n"
        f"{history_text}"
        f"Requested tone: {tone}\n\n"
        "Please output a JSON object ONLY with keys: label, tone, draft, suggested_action_items.\n"
        "Example: {\"label\":\"formal_1\",\"tone\":\"formal\",\"draft\":\"...\",\"suggested_action_items\":[\"...\",\"...\"]}\n"
        f"{instructions}"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]
    return messages
