# Changelog

All notable changes to this project are documented in this file.
Format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased] — Week 1

### Added

- Problem_Statement.md finalized (Project #59 — Internship & Campus Hiring Platform)
- Repository scaffold: FastAPI backend skeleton, SQLAlchemy models, CI workflow
- Root files: .gitignore, LICENSE (MIT), .env.example, README.md, COMMIT_TRACKER.md
- docs/db-schema.md: initial 8-table schema with relationships

### Day 11 (Review-I)

- Architecture, ER, and class/module diagrams under docs/diagrams/ (.md + rendered .png)
- Auth flow issuing JWT (login / signup / me endpoints)
- Student, company, and admin API modules wired end-to-end
- Backend test suite (pytest) and CI lint + test pipeline (black, flake8)
- React frontend (Vite + Bootstrap): login, signup, student and company dashboards
- Student flow: browse and apply to internship posts
- Company flow: post and manage internship openings

## [Unreleased] — Week 2 (Review-II hardening)

### Security

- `BCRYPT_ROUNDS` actually wired into the password hash context
- JWT `sub` parsing guards non-integer subjects (401, no 500s)
- Production refuses to boot with placeholder `SECRET_KEY`
- CORS tightened to explicit methods/headers; LIKE-wildcard escaping on browse
- Schema bounds on profiles, posts, skills, cover notes; skill normalization

### Tests

- 25 new tests (`test_review2.py`, `test_email.py`): 46 total, 95% coverage
- Coverage gate `--cov-fail-under=85` in backend CI; Postgres 15 CI service
  with `DATABASE_URL` switch in `tests/conftest.py`

### Enhancements

- SMTP status-change notifications (`app/services/email.py`, no-op unconfigured)
- Frontend prod readiness: `VITE_API_URL`, 401 auto-logout, `vercel.json`
  SPA rewrites, dashboard error handling + close/reopen, `render.yaml`
- `exercises/` evidence folders: fastapi, react, sql, testing, deployment, agile

### Day 41 (Review-II)

- Admin backend completed: `GET /admin/applications` overview plus
  `DELETE /admin/posts/{id}` and `DELETE /admin/users/{id}` (self-delete
  guarded) in `app/services/admin.py` + `app/api/admin.py`
- Admin UI: `AdminDashboard.jsx` with users/posts/applications overview and
  manage deletes, `/admin` route, role-aware redirects (Navbar + Login)
- Logging: signup/login warnings + admin delete audit in services,
  `basicConfig` + unhandled-exception logger in `app/main.py`
- CORS: `DELETE` added to allowed methods for admin manage actions
- CI/CD: Render deploy-hook job (`backend.yml`) and Vercel deploy job
  (`frontend.yml`), both skipped silently without repo secrets
- Tests: 48 passing (admin overview + manage deletes, self-delete guard,
  new-endpoint role matrix); black + flake8 clean, frontend build clean
- Docs: README Live Demo/Video + Screenshots sections, admin endpoint table,
  as-built architecture diagram (Vercel/Render/email/admin), this entry