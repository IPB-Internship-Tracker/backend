from email.message import EmailMessage

from app import email as email_module


class FakeSMTP:
    sent_messages: list[EmailMessage] = []
    started_tls = False
    login_data: tuple[str, str] | None = None

    def __init__(self, host: str, port: int, timeout: int) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def __enter__(self) -> "FakeSMTP":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def starttls(self) -> None:
        FakeSMTP.started_tls = True

    def login(self, username: str, password: str) -> None:
        FakeSMTP.login_data = (username, password)

    def send_message(self, message: EmailMessage) -> None:
        FakeSMTP.sent_messages.append(message)


def test_send_notification_email_skip_jika_belum_dikonfigurasi(monkeypatch):
    monkeypatch.setattr(email_module.settings, "email_notifications_enabled", False)

    sent = email_module.send_notification_email(
        to_email="budi@apps.ipb.ac.id",
        subject="Status Lamaran",
        message="Lamaran diterima",
    )

    assert sent is False


def test_send_notification_email_smtp_berhasil(monkeypatch):
    FakeSMTP.sent_messages = []
    FakeSMTP.started_tls = False
    FakeSMTP.login_data = None

    monkeypatch.setattr(email_module.settings, "email_notifications_enabled", True)
    monkeypatch.setattr(email_module.settings, "smtp_host", "smtp.test.local")
    monkeypatch.setattr(email_module.settings, "smtp_port", 587)
    monkeypatch.setattr(email_module.settings, "smtp_username", "mailer")
    monkeypatch.setattr(email_module.settings, "smtp_password", "secret")
    monkeypatch.setattr(email_module.settings, "smtp_from_email", "noreply@test.local")
    monkeypatch.setattr(email_module.settings, "smtp_from_name", "IPB Tracker")
    monkeypatch.setattr(email_module.settings, "smtp_use_tls", True)
    monkeypatch.setattr(email_module.smtplib, "SMTP", FakeSMTP)

    sent = email_module.send_notification_email(
        to_email="budi@apps.ipb.ac.id",
        subject="Status Lamaran",
        message="Lamaran diterima",
    )

    assert sent is True
    assert FakeSMTP.started_tls is True
    assert FakeSMTP.login_data == ("mailer", "secret")
    assert len(FakeSMTP.sent_messages) == 1
    message = FakeSMTP.sent_messages[0]
    assert message["To"] == "budi@apps.ipb.ac.id"
    assert message["Subject"] == "Status Lamaran"
    assert "Lamaran diterima" in message.get_content()
