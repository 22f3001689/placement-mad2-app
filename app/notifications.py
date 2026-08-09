"""Email delivery: renders a stored EmailTemplate and sends it via SMTP, or
logs the rendered content if no SMTP server is configured.
"""

import smtplib
from email.message import EmailMessage

from flask import current_app

from app.models import EmailTemplate
from app.utils import get_logger

logger = get_logger(__name__)


def send_email(to_email, template_key, context):
    """Renders EmailTemplate[template_key] with context and sends/logs it.

    Never raises - a delivery failure is logged, not surfaced to the caller.
    """
    template = EmailTemplate.query.filter_by(key=template_key).first()
    if template is None:
        logger.warning(
            "No EmailTemplate found for key=%s - skipping send", template_key
        )
        return

    if not to_email:
        logger.info("Skipping %s email - recipient has no email on file", template_key)
        return

    subject = template.subject.format(**context)
    body = template.body.format(**context)

    mail_server = current_app.config.get("MAIL_SERVER")
    if not mail_server:
        logger.info(
            "Email (log fallback) to=%s subject=%r body=%r", to_email, subject, body
        )
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(mail_server, current_app.config["MAIL_PORT"]) as server:
            if current_app.config.get("MAIL_USE_TLS"):
                server.starttls()
            username = current_app.config.get("MAIL_USERNAME")
            password = current_app.config.get("MAIL_PASSWORD")
            if username and password:
                server.login(username, password)
            server.send_message(message)
        logger.info("Email sent: to=%s subject=%r", to_email, subject)
    except Exception:
        logger.exception("Failed to send email to=%s subject=%r", to_email, subject)
