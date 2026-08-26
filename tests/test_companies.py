from tests.conftest import auth_header, register_company, register_student


def _login(client, email, password="secret123"):
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return auth_header(res.json()["access_token"])


def _company_with_post(client, title="Data Analyst Intern"):
    register_company(client)
    headers = _login(client, "company@test.com")
    post = client.post(
        "/api/v1/companies/posts",
        headers=headers,
        json={
            "title": title,
            "description": "Analyze internship data",
            "location": "Bangalore",
            "internship_type": "Remote",
            "duration": "3 months",
            "stipend": "15000",
            "skills": ["sql", "python"],
        },
    ).json()
    return headers, post


def _student_apply(client, post_id):
    register_student(client)
    headers = _login(client, "student@test.com")
    client.post(
        "/api/v1/students/applications",
        headers=headers,
        json={"post_id": post_id, "cover_note": "Interested"},
    )
    return headers


def test_company_updates_profile(client):
    register_company(client)
    headers = _login(client, "company@test.com")
    res = client.patch(
        "/api/v1/companies/profile",
        headers=headers,
        json={"industry": "IT Services", "website": "https://testcorp.com"},
    )
    assert res.status_code == 200
    assert res.json()["industry"] == "IT Services"


def test_company_creates_and_lists_posts(client):
    headers, post = _company_with_post(client)
    assert post["title"] == "Data Analyst Intern"
    assert set(post["skills"]) == {"sql", "python"}

    posts = client.get("/api/v1/companies/posts", headers=headers).json()
    assert len(posts) == 1


def test_company_closes_post(client):
    headers, post = _company_with_post(client)
    res = client.patch(
        f"/api/v1/companies/posts/{post['id']}",
        headers=headers,
        json={"is_open": False},
    )
    assert res.status_code == 200
    assert res.json()["is_open"] is False


def test_company_sees_applicants_and_advances_status(client):
    company_headers, post = _company_with_post(client)
    student_headers = _student_apply(client, post["id"])

    applicants = client.get(
        f"/api/v1/companies/posts/{post['id']}/applicants", headers=company_headers
    ).json()
    assert len(applicants) == 1
    assert applicants[0]["student_name"] == "Test Student"
    assert applicants[0]["status"] == "applied"

    application_id = applicants[0]["id"]
    for new_status in ("shortlisted", "interview", "selected"):
        res = client.patch(
            f"/api/v1/companies/applications/{application_id}/status",
            headers=company_headers,
            json={"status": new_status},
        )
        assert res.status_code == 200
        assert res.json()["status"] == new_status

    # Student dashboard reflects the final status.
    mine = client.get("/api/v1/students/applications", headers=student_headers).json()
    assert len(mine) == 1
    assert mine[0]["status"] == "selected"
    assert mine[0]["post_title"] == post["title"]


def test_company_cannot_update_other_companys_application(client):
    company_headers, post = _company_with_post(client)
    _student_apply(client, post["id"])

    register_company(client, email="other@test.com", name="Other Corp")
    other_headers = _login(client, "other@test.com")
    application_id = client.get(
        f"/api/v1/companies/posts/{post['id']}/applicants", headers=company_headers
    ).json()[0]["id"]

    res = client.patch(
        f"/api/v1/companies/applications/{application_id}/status",
        headers=other_headers,
        json={"status": "selected"},
    )
    assert res.status_code == 403


def test_company_rejects_invalid_status(client):
    company_headers, post = _company_with_post(client)
    _student_apply(client, post["id"])

    application_id = client.get(
        f"/api/v1/companies/posts/{post['id']}/applicants", headers=company_headers
    ).json()[0]["id"]

    res = client.patch(
        f"/api/v1/companies/applications/{application_id}/status",
        headers=company_headers,
        json={"status": "hired"},
    )
    assert res.status_code == 422
