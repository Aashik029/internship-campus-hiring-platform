from tests.conftest import auth_header, register_company, register_student


def _login(client, email, password="secret123"):
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return auth_header(res.json()["access_token"])


def _create_post(client, headers):
    return client.post(
        "/api/v1/companies/posts",
        headers=headers,
        json={
            "title": "Python Backend Intern",
            "description": "Build FastAPI services",
            "location": "Chennai",
            "internship_type": "Hybrid",
            "duration": "6 months",
            "stipend": "20000",
            "skills": ["python", "fastapi"],
        },
    )


def test_student_updates_profile(client):
    register_student(client)
    headers = _login(client, "student@test.com")
    res = client.patch(
        "/api/v1/students/profile",
        headers=headers,
        json={"bio": "CSE final year", "education": "B.E. CSE"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["bio"] == "CSE final year"
    assert body["education"] == "B.E. CSE"


def test_student_adds_and_lists_skills(client):
    register_student(client)
    headers = _login(client, "student@test.com")
    for name in ("python", "SQL"):
        res = client.post(
            "/api/v1/students/skills", headers=headers, json={"name": name}
        )
        assert res.status_code == 201

    skills = client.get("/api/v1/students/skills", headers=headers).json()
    assert {s["name"] for s in skills} == {"python", "SQL"}


def test_student_browses_open_posts(client):
    register_student(client)
    register_company(client)
    company_headers = _login(client, "company@test.com")
    _create_post(client, company_headers)

    student_headers = _login(client, "student@test.com")
    posts = client.get("/api/v1/students/posts", headers=student_headers).json()
    assert len(posts) == 1
    assert posts[0]["title"] == "Python Backend Intern"
    assert set(posts[0]["skills"]) == {"python", "fastapi"}


def test_student_browses_posts_with_skill_filter(client):
    register_student(client)
    register_company(client)
    company_headers = _login(client, "company@test.com")
    _create_post(client, company_headers)

    student_headers = _login(client, "student@test.com")
    matches = client.get(
        "/api/v1/students/posts", headers=student_headers, params={"skill": "python"}
    ).json()
    assert len(matches) == 1
    no_match = client.get(
        "/api/v1/students/posts", headers=student_headers, params={"skill": "rust"}
    ).json()
    assert no_match == []


def test_student_applies_and_sees_status(client):
    register_student(client)
    register_company(client)
    company_headers = _login(client, "company@test.com")
    post = _create_post(client, company_headers).json()

    student_headers = _login(client, "student@test.com")
    res = client.post(
        "/api/v1/students/applications",
        headers=student_headers,
        json={"post_id": post["id"], "cover_note": "Eager to learn"},
    )
    assert res.status_code == 201
    assert res.json()["status"] == "applied"

    apps = client.get("/api/v1/students/applications", headers=student_headers).json()
    assert len(apps) == 1
    assert apps[0]["post_id"] == post["id"]


def test_student_cannot_apply_twice(client):
    register_student(client)
    register_company(client)
    company_headers = _login(client, "company@test.com")
    post = _create_post(client, company_headers).json()

    student_headers = _login(client, "student@test.com")
    payload = {"post_id": post["id"], "cover_note": "first"}
    assert (
        client.post(
            "/api/v1/students/applications", headers=student_headers, json=payload
        ).status_code
        == 201
    )
    res = client.post(
        "/api/v1/students/applications", headers=student_headers, json=payload
    )
    assert res.status_code == 400
