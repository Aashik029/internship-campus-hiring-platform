from tests.conftest import auth_header, register_company, register_student


def test_register_student_creates_profile(client):
    res = register_student(client)
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "student@test.com"
    assert body["role"] == "student"
    assert body["id"] > 0


def test_register_company_creates_company(client):
    res = register_company(client)
    assert res.status_code == 201
    assert res.json()["role"] == "company"


def test_register_duplicate_email_fails(client):
    register_student(client)
    res = register_student(client)
    assert res.status_code == 400


def test_login_returns_jwt_and_me_works(client):
    register_student(client)
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "student@test.com", "password": "secret123"},
    )
    assert res.status_code == 200
    token = res.json()["access_token"]
    assert token

    me = client.get("/api/v1/auth/me", headers=auth_header(token))
    assert me.status_code == 200
    assert me.json()["email"] == "student@test.com"


def test_login_wrong_password_fails(client):
    register_student(client)
    res = client.post(
        "/api/v1/auth/login", json={"email": "student@test.com", "password": "wrong"}
    )
    assert res.status_code == 401


def test_me_without_token_fails(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_me_with_bad_token_fails(client):
    res = client.get("/api/v1/auth/me", headers=auth_header("not.a.jwt"))
    assert res.status_code == 401
