"""Deadline-reminder delivery — same pluggable-provider shape as services/sms.py.
NOTIFY_PROVIDER=console (default, logs the reminder, no account needed) | smtp
(any real mailbox — Gmail's free SMTP relay works fine at this volume, genuinely
open source: Python's stdlib smtplib/email, no paid email API). WhatsApp becomes a
third option here once that channel exists — this module is the one place a
reminder "send" call happens, so adding it later doesn't touch the scheduler."""

import logging
import smtplib
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger("lawgic.notifications")


async def send_deadline_reminder(to_email: str, subject: str, body: str) -> None:
    if settings.NOTIFY_PROVIDER == "smtp":
        await _send_via_smtp(to_email, subject, body)
    else:
        # print(), not logger — a bare logger here has no configured handler/level and
        # would silently drop this (same lesson as services/sms.py).
        print(f"[dev notify -> {to_email}] {subject}\n{body}", flush=True)


async def _send_via_smtp(to_email: str, subject: str, body: str) -> None:
    if not (settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD):
        raise RuntimeError(
            "NOTIFY_PROVIDER=smtp requires SMTP_HOST, SMTP_USER, SMTP_PASSWORD "
            "(see backend/.env.example)."
        )
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
    msg["To"] = to_email

    # smtplib is blocking stdlib — this only runs once a day from the scheduler
    # (core/scheduler.py), not on a request path, so a short blocking call is fine.
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
