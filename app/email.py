import logging
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from app.config import settings


logger = logging.getLogger(__name__)


def _email_configured() -> bool:
    return bool(
        settings.email_notifications_enabled
        and settings.smtp_host
        and settings.smtp_from_email
    )


def send_notification_email(
    *,
    to_email: str,
    subject: str,
    message: str,
) -> bool:
    """Kirim notifikasi email via SMTP.

    Return False kalau fitur email belum dikonfigurasi atau pengiriman gagal.
    """
    if not _email_configured():
        logger.info("Email notification skipped: SMTP belum dikonfigurasi")
        return False

    email = EmailMessage()
    email["Subject"] = subject
    email["From"] = formataddr((settings.smtp_from_name, settings.smtp_from_email))
    email["To"] = to_email
    email.set_content(message)

    try:
        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
            timeout=settings.smtp_timeout_seconds,
        ) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(email)
    except Exception:
        logger.exception("Gagal mengirim email notifikasi ke %s", to_email)
        return False

    return True
