"""Review-II gap tests: admin, role matrix, JWT edges, negatives, config."""

from datetime import timedelta

from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from tests.conftest import (
    TestingSessionLocal,
    auth_header,
    register_company,
    register_student,
)


def _login(client, email, password="secret123"):
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    return res.json()["access_token"]


def _seed_admin(email="admin@test.com", password="admin123"):
    from app.models import User

    db = TestingSessionLocal()
    try:
        db.add(
            User(
                email=email,
                password_hash=hash_password(password),
                full_name="Admin",
                role="admin",
            )
        )
        db.commit()
    finally:
        db.close()


def _company_token(client, email="company@test.com"):
    register_company(client, email=email)
    return _login(client, email)


def _student_token(client, email="student@test.com"):
    register_student(client, email=email)
    return _login(client, email)


def _make_post(client, token, title="Backend Intern", **overrides):
    payload = {
        "title": title,
        "description": "Learn backend development",
        "location": "Remote",
        "skills": ["Python"],
    }
    payload.update(overrides)
    res = client.post(
        "/api/v1/companies/posts", json=payload, headers=auth_header(token)
    )
    assert res.status_code == 201, res.text
    return res.json()


# --- Admin (was 0% covered) ---


def test_admin_lists_users_and_posts(client):
    _seed_admin()
    register_student(client)
    token = _login(client, "admin@test.com", "admin123")

    users = client.get("/api/v1/admin/users", headers=auth_header(token))
    assert users.status_code == 200
    assert {u["email"] for u in users.json()} >= {"admin@test.com", "student@test.com"}

    posts = client.get("/api/v1/admin/posts", headers=auth_header(token))
    assert posts.status_code == 200
    assert posts.json() == []


def test_admin_guarded_from_students_and_anonymous(client):
    _seed_admin()
    student = _student_token(client)
    assert (
        client.get("/api/v1/admin/users", headers=auth_header(student)).status_code
        == 403
    )
    assert (
        client.get("/api/v1/admin/posts", headers=auth_header(student)).status_code
        == 403
    )
    assert (
        client.get(
            "/api/v1/admin/applications", headers=auth_header(student)
        ).status_code
        == 403
    )
    assert client.get("/api/v1/admin/users").status_code == 401
    assert client.get("/api/v1/admin/applications").status_code == 401


def test_admin_applications_overview_and_manage_deletes(client):
    _seed_admin()
    company = _company_token(client)
    student = _student_token(client, email="managed@test.com")
    post = _make_post(client, company, title="Managed Intern")
    applied = client.post(
        "/api/v1/students/applications",
        json={"post_id": post["id"]},
        headers=auth_header(student),
    )
    assert applied.status_code == 201

    admin = _login(client, "admin@test.com", "admin123")
    overview = client.get("/api/v1/admin/applications", headers=auth_header(admin))
    assert overview.status_code == 200
    rows = overview.json()
    assert len(rows) == 1
    assert rows[0]["post_title"] == "Managed Intern"
    assert rows[0]["student_email"] == "managed@test.com"

    # Delete post cascades its application.
    deleted = client.delete(
        f"/api/v1/admin/posts/{post['id']}", headers=auth_header(admin)
    )
    assert deleted.status_code == 204
    assert client.get("/api/v1/admin/posts", headers=auth_header(admin)).json() == []
    assert (
        client.get("/api/v1/admin/applications", headers=auth_header(admin)).json()
        == []
    )
    assert (
        client.delete(
            "/api/v1/admin/posts/999999", headers=auth_header(admin)
        ).status_code
        == 404
    )

    # Delete user removes their account.
    users = client.get("/api/v1/admin/users", headers=auth_header(admin)).json()
    victim = next(u for u in users if u["email"] == "managed@test.com")
    removed = client.delete(
        f"/api/v1/admin/users/{victim['id']}", headers=auth_header(admin)
    )
    assert removed.status_code == 204
    remaining = client.get("/api/v1/admin/users", headers=auth_header(admin)).json()
    assert "managed@test.com" not in {u["email"] for u in remaining}
    assert (
        client.delete(
            "/api/v1/admin/users/999999", headers=auth_header(admin)
        ).status_code
        == 404
    )


def test_admin_cannot_delete_self(client):
    _seed_admin()
    admin = _login(client, "admin@test.com", "admin123")
    me = client.get("/api/v1/auth/me", headers=auth_header(admin)).json()
    res = client.delete(f"/api/v1/admin/users/{me['id']}", headers=auth_header(admin))
    assert res.status_code == 400


# --- Role-guard matrix ---


def test_student_cannot_touch_company_routes(client):
    token = _student_token(client)
    assert (
        client.get("/api/v1/companies/profile", headers=auth_header(token)).status_code
        == 403
    )
    res = client.post(
        "/api/v1/companies/posts",
        json={"title": "X", "description": "Y"},
        headers=auth_header(token),
    )
    assert res.status_code == 403


def test_company_cannot_touch_student_routes(client):
    token = _company_token(client)
    assert (
        client.get("/api/v1/students/profile", headers=auth_header(token)).status_code
        == 403
    )
    res = client.post(
        "/api/v1/students/applications",
        json={"post_id": 1},
        headers=auth_header(token),
    )
    assert res.status_code == 403


# --- JWT edges ---


def test_expired_token_rejected(client):
    register_student(client, email="exp@test.com")
    token = _login(client, "exp@test.com")
    me = client.get("/api/v1/auth/me", headers=auth_header(token))
    user_id = str(me.json()["id"])
    expired = create_access_token(user_id, timedelta(minutes=-1))
    res = client.get("/api/v1/auth/me", headers=auth_header(expired))
    assert res.status_code == 401


def test_non_integer_subject_rejected_without_500(client):
    register_student(client)
    forged = jwt.encode(
        {"sub": "not-an-int"}, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    res = client.get("/api/v1/auth/me", headers=auth_header(forged))
    assert res.status_code == 401


def test_tampered_signature_rejected(client):
    register_student(client)
    token = _login(client, "student@test.com")
    tampered = token[:-2] + ("ab" if not token.endswith("ab") else "cd")
    res = client.get("/api/v1/auth/me", headers=auth_header(tampered))
    assert res.status_code == 401


# --- Auth validation ---


def test_register_admin_role_rejected(client):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "root@test.com",
            "password": "secret123",
            "full_name": "Root",
            "role": "admin",
        },
    )
    assert res.status_code == 422


def test_register_bad_email_and_short_password_rejected(client):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "secret123",
            "full_name": "Bad",
            "role": "student",
        },
    )
    assert res.status_code == 422
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "short@test.com",
            "password": "123",
            "full_name": "Short",
            "role": "student",
        },
    )
    assert res.status_code == 422


def test_login_unknown_email_fails(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@test.com", "password": "secret123"},
    )
    assert res.status_code == 401


# --- Student negatives ---


def test_apply_to_closed_or_missing_post(client):
    company = _company_token(client)
    student = _student_token(client, email="s2@test.com")
    post = _make_post(client, company)
    res = client.post(
        "/api/v1/students/applications",
        json={"post_id": 999999},
        headers=auth_header(student),
    )
    assert res.status_code == 404

    close = client.patch(
        f"/api/v1/companies/posts/{post['id']}",
        json={"is_open": False},
        headers=auth_header(company),
    )
    assert close.status_code == 200
    res = client.post(
        "/api/v1/students/applications",
        json={"post_id": post["id"]},
        headers=auth_header(student),
    )
    assert res.status_code == 400

    # Closed posts stay hidden from browse.
    browse = client.get("/api/v1/students/posts", headers=auth_header(student))
    assert browse.status_code == 200
    assert post["id"] not in {p["id"] for p in browse.json()}


def test_duplicate_skill_is_idempotent(client):
    token = _student_token(client)
    first = client.post(
        "/api/v1/students/skills",
        json={"name": "Python"},
        headers=auth_header(token),
    )
    assert first.status_code == 201
    second = client.post(
        "/api/v1/students/skills",
        json={"name": "  python  "},
        headers=auth_header(token),
    )
    assert second.status_code == 201
    assert second.json()["id"] == first.json()["id"]
    assert (
        client.post(
            "/api/v1/students/skills",
            json={"name": "   "},
            headers=auth_header(token),
        ).status_code
        == 422
    )


def test_search_wildcards_do_not_break_browse(client):
    company = _company_token(client)
    student = _student_token(client, email="s3@test.com")
    post = _make_post(client, company, title="100% match_test")
    res = client.get(
        "/api/v1/students/posts",
        params={"query": "%_"},
        headers=auth_header(student),
    )
    assert res.status_code == 200
    assert post["id"] not in {p["id"] for p in res.json()}


# --- Company negatives ---


def test_company_cannot_patch_other_companys_post(client):
    c1 = _company_token(client, email="c1@test.com")
    c2 = _company_token(client, email="c2@test.com")
    post = _make_post(client, c1)
    res = client.patch(
        f"/api/v1/companies/posts/{post['id']}",
        json={"title": "Hijacked"},
        headers=auth_header(c2),
    )
    assert res.status_code == 404


def test_create_post_missing_title_rejected(client):
    token = _company_token(client)
    res = client.post(
        "/api/v1/companies/posts",
        json={"description": "No title here"},
        headers=auth_header(token),
    )
    assert res.status_code == 422


def test_create_post_rejects_too_many_skills(client):
    token = _company_token(client)
    res = client.post(
        "/api/v1/companies/posts",
        json={
            "title": "T",
            "description": "D",
            "skills": [f"skill-{i}" for i in range(21)],
        },
        headers=auth_header(token),
    )
    assert res.status_code == 422


def test_close_and_reopen_flow(client):
    token = _company_token(client)
    post = _make_post(client, token)
    assert post["is_open"] is True
    closed = client.patch(
        f"/api/v1/companies/posts/{post['id']}",
        json={"is_open": False},
        headers=auth_header(token),
    )
    assert closed.json()["is_open"] is False
    reopened = client.patch(
        f"/api/v1/companies/posts/{post['id']}",
        json={"is_open": True},
        headers=auth_header(token),
    )
    assert reopened.json()["is_open"] is True


def test_applicants_empty_then_status_advance(client):
    company = _company_token(client)
    student = _student_token(client, email="s4@test.com")
    post = _make_post(client, company)
    empty = client.get(
        f"/api/v1/companies/posts/{post['id']}/applicants",
        headers=auth_header(company),
    )
    assert empty.status_code == 200
    assert empty.json() == []

    applied = client.post(
        "/api/v1/students/applications",
        json={"post_id": post["id"], "cover_note": "Excited to apply"},
        headers=auth_header(student),
    )
    assert applied.status_code == 201

    full = client.get(
        f"/api/v1/companies/posts/{post['id']}/applicants",
        headers=auth_header(company),
    )
    assert len(full.json()) == 1
    app_id = full.json()[0]["id"]
    advanced = client.patch(
        f"/api/v1/companies/applications/{app_id}/status",
        json={"status": "shortlisted"},
        headers=auth_header(company),
    )
    assert advanced.status_code == 200
    assert advanced.json()["status"] == "shortlisted"


# --- Input bounds ---


def test_oversized_profile_and_note_rejected(client):
    student = _student_token(client)
    res = client.patch(
        "/api/v1/students/profile",
        json={"bio": "x" * 2001},
        headers=auth_header(student),
    )
    assert res.status_code == 422

    company = _company_token(client, email="cb@test.com")
    post = _make_post(client, company)
    res = client.post(
        "/api/v1/students/applications",
        json={"post_id": post["id"], "cover_note": "y" * 2001},
        headers=auth_header(student),
    )
    assert res.status_code == 422


# --- Config ---


def test_cors_origins_split_and_trim():
    from app.core.config import Settings

    s = Settings(BACKEND_CORS_ORIGINS=" https://a.example,https://b.example ,, ")
    assert s.cors_origins == ["https://a.example", "https://b.example"]


def test_production_secret_guard():
    from app.core.config import Settings

    prod = Settings(APP_ENV="production", SECRET_KEY="change-me")
    try:
        prod.ensure_production_secrets()
    except RuntimeError:
        pass
    else:  # pragma: no cover
        raise AssertionError("production with placeholder SECRET_KEY must fail")

    dev = Settings(APP_ENV="development", SECRET_KEY="change-me")
    dev.ensure_production_secrets()  # must not raise

    strong = Settings(APP_ENV="production", SECRET_KEY="x" * 64)
    strong.ensure_production_secrets()  # must not raise
