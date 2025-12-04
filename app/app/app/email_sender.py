import os
import aiosmtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT") or 587)
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL") or SMTP_USER
SMTP_SECURE = os.getenv("SMTP_SECURE", "false").lower() == "true"

async def send_email(to_email: str, subject: str, body_text: str, from_name: str = None):
    if not SMTP_HOST or not SMTP_USER:
        raise RuntimeError("SMTP configuration missing in env")

    msg = EmailMessage()
    sender = f"{from_name} <{FROM_EMAIL}>" if from_name else FROM_EMAIL
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject or "(no subject)"
    msg.set_content(body_text)

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASS,
        use_tls=SMTP_SECURE
    )
