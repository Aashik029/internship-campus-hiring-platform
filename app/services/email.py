"""Transactional email helpers (SMTP).

All helpers are no-ops when SMTP is not configured (``SMTP_HOST`` empty),
so local development and the test suite never require a mail server.
"""

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_FROM)


def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text email. Returns True if handed to SMTP, else False."""
    if not is_configured():
        logger.info("Email not configured; skipping send to %s (%s)", to, subject)
        return False

    message = EmailMessage()
    message["From"] = settings.SMTP_FROM
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
        smtp.starttls()
        if settings.SMTP_USER:
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(message)
    return True


def notify_status_change(
    student_email: str,
    student_name: str,
    post_title: str,
    company_name: str,
    new_status: str,
) -> bool:
    """Notify a student that a company updated their application status."""
    subject = f"Application update: {post_title} → {new_status}"
    body = (
        f"Hi {student_name},\n\n"
        f"{company_name} updated your application for '{post_title}' "
        f"to: {new_status}.\n\n"
        "Good luck!\nInternship & Campus Hiring Platform"
    )
    return send_email(student_email, subject, body)
