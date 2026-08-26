"""Email enhancement: no-op without SMTP, hook fires on status change."""

import app.services.companies as company_service
from app.core.config import settings
from app.services import email as email_service
from tests.conftest import auth_header, register_company, register_student


def _setup_application(client):
    register_company(client, email="mailco@test.com")
    register_student(client, email="mailstudent@test.com")
    co = client.post(
        "/api/v1/auth/login",
        json={"email": "mailco@test.com", "password": "secret123"},
    ).json()["access_token"]
    st = client.post(
        "/api/v1/auth/login",
        json={"email": "mailstudent@test.com", "password": "secret123"},
    ).json()["access_token"]
    post = client.post(
        "/api/v1/companies/posts",
        json={"title": "QA Intern", "description": "Test things"},
        headers=auth_header(co),
    ).json()
    client.post(
        "/api/v1/students/applications",
        json={"post_id": post["id"]},
        headers=auth_header(st),
    )
    app_id = client.get(
        f"/api/v1/companies/posts/{post['id']}/applicants",
        headers=auth_header(co),
    ).json()[0]["id"]
    return co, app_id


def test_send_email_noop_without_smtp():
    assert settings.SMTP_HOST == "" or email_service.is_configured() is False
    assert email_service.send_email("a@b.c", "Hi", "Body") is False
    assert (
        email_service.notify_status_change("a@b.c", "A", "Post", "Co", "hired") is False
    )


def test_status_change_triggers_notification(client, monkeypatch):
    calls = []
    monkeypatch.setattr(
        company_service,
        "notify_status_change",
        lambda **kwargs: calls.append(kwargs) or True,
    )
    co, app_id = _setup_application(client)
    res = client.patch(
        f"/api/v1/companies/applications/{app_id}/status",
        json={"status": "interview"},
        headers=auth_header(co),
    )
    assert res.status_code == 200
    assert len(calls) == 1
    assert calls[0]["student_email"] == "mailstudent@test.com"
    assert calls[0]["new_status"] == "interview"
    assert calls[0]["post_title"] == "QA Intern"


def test_email_failure_does_not_break_status_update(client, monkeypatch):
    def _boom(**kwargs):
        raise ConnectionError("smtp down")

    monkeypatch.setattr(company_service, "notify_status_change", _boom)
    co, app_id = _setup_application(client)
    res = client.patch(
        f"/api/v1/companies/applications/{app_id}/status",
        json={"status": "selected"},
        headers=auth_header(co),
    )
    assert res.status_code == 200
    assert res.json()["status"] == "selected"


def test_send_email_uses_smtp_when_configured(monkeypatch):
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.test")
    monkeypatch.setattr(settings, "SMTP_PORT", 587)
    monkeypatch.setattr(settings, "SMTP_USER", "")
    monkeypatch.setattr(settings, "SMTP_FROM", "noreply@test.com")

    sent = {}

    class FakeSMTP:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def starttls(self):
            sent["tls"] = True

        def send_message(self, message):
            sent["message"] = message

    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)
    assert email_service.send_email("to@test.com", "Subject", "Hello") is True
    assert sent["tls"] is True
    assert sent["message"]["To"] == "to@test.com"
    assert sent["message"]["Subject"] == "Subject"
