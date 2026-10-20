"""Minimal SMTP mailer. If MAIL_SERVER isn't set, mails are logged instead of sent."""
import smtplib
from email.message import EmailMessage

from flask import current_app


def send_mail(to, subject, body):
    cfg = current_app.config
    if not to:
        return False
    if not cfg.get("MAIL_SERVER"):
        current_app.logger.info("MAIL (not sent, MAIL_SERVER unset) to=%s subject=%s\n%s", to, subject, body)
        return False
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = cfg["MAIL_FROM"], to, subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=15) as s:
            s.starttls()
            if cfg.get("MAIL_USERNAME"):
                s.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
            s.send_message(msg)
        return True
    except Exception as exc:  # never break a booking because email failed
        current_app.logger.warning("Mail failed: %s", exc)
        return False
