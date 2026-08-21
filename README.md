# Internship & Campus Hiring Platform

A full-stack platform that connects students looking for internships with companies that want to hire interns.

## Live Demo + Video

- Frontend (Vercel): https://internship-campus-hiring.vercel.app
- Backend (Render): https://internship-campus-hiring-platform-2.onrender.com — health: `/api/v1/health`
- Demo video: _link added after recording_

## Overview

Students create profiles with skills, search internship posts, apply, and track application status (Applied → Shortlisted → Interview → Selected). Companies register, post internships with required skills, and manage applicants. An admin oversees users, posts, and applications.

## Tech Stack

| Layer   | Technology                                   |
| ------- | -------------------------------------------- |
| Backend | Python 3.12, FastAPI, SQLAlchemy, JWT, bcrypt |
| Frontend| React.js + Bootstrap + Axios (Vite)          |
| Database| PostgreSQL (SQLite fallback for local dev)    |
| CI/CD   | GitHub Actions                               |
| Hosting | Render (backend, via `render.yaml`), Vercel (frontend, via `frontend/vercel.json`) |

## Features

- Student: register, profile, skills, browse/search internships, apply, status board
- Company: register, profile, post internships, view applicants, update status (emails student)
- Admin: overview users/posts/applications + delete posts/users (`/admin` dashboard)
- Skills matching between post requirements and student skills

## Screenshots

_Add after first run: `docs/screenshots/student-dashboard.png`,
`docs/screenshots/company-dashboard.png`, `docs/screenshots/admin-dashboard.png`._

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+ (for the frontend)
- Git

### Setup

```bash
git clone https://github.com/AashikTech/internship-campus-hiring-platform.git
cd internship-campus-hiring-platform
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

### Environment

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux
# edit .env: set SECRET_KEY and DATABASE_URL
```

### Run the backend

```bash
uvicorn app.main:app --reload
```

- Interactive API docs (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

### Run the frontend

Open a second terminal (keep the backend running):

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173
- The frontend calls the backend on `http://localhost:8000` (Vite proxy) and is already allowed by the backend CORS config.

### Database (PostgreSQL)

The project runs on **PostgreSQL 15**. The fastest way to start a local instance is Docker:

```bash
docker compose up -d
```

- DB name: `hiring_platform`
- User / password: `postgres` / `postgres`
- Port: `5432`

Then set `DATABASE_URL` in `.env` to:

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/hiring_platform
```

If `DATABASE_URL` is left empty the app falls back to a local SQLite file for quick testing.

### Run the tests

```bash
pytest -v
```

### Lint

```bash
black --check app tests
flake8 app tests
```

## Environment Variables

| Variable                 | Description                     | Required |
| ------------------------ | ------------------------------- | -------- |
| SECRET_KEY               | JWT signing key                 | Yes      |
| DATABASE_URL             | DB connection string            | No*      |
| JWT_ALGORITHM            | HS256                           | No       |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token lifetime               | No       |
| BACKEND_CORS_ORIGINS     | Allowed frontend origins        | No       |
| SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASSWORD / SMTP_FROM | Status-change email (empty `SMTP_HOST` disables sending) | No |

\* Falls back to local SQLite if empty.

## API Endpoints

All endpoints live under `/api/v1`. Every response uses a consistent JSON shape where applicable and the correct HTTP status codes. Full reference: [API contract](docs/diagrams/api-contract.md).

### Auth (`/auth`)

| Method | Path      | Description                              | Auth   |
| ------ | --------- | ---------------------------------------- | ------ |
| POST   | /register | Register as student or company (201)     | Public |
| POST   | /login    | Get JWT access token                     | Public |
| GET    | /me       | Current user profile                     | Bearer |

### Student (`/students`)

| Method | Path                | Description                         | Auth           |
| ------ | ------------------- | ----------------------------------- | -------------- |
| GET    | /profile            | Own student profile                 | student        |
| PATCH  | /profile            | Update bio/education/resume_url/phone | student      |
| GET    | /skills             | List own skills                     | student        |
| POST   | /skills             | Add a skill (201)                   | student        |
| GET    | /posts              | Browse open posts (query/location/skill filters) | student |
| POST   | /applications       | Apply to a post (201)               | student        |
| GET    | /applications       | Application status board            | student        |

### Company (`/companies`)

| Method | Path                              | Description                | Auth           |
| ------ | --------------------------------- | -------------------------- | -------------- |
| GET    | /profile                          | Own company profile        | company        |
| PATCH  | /profile                          | Update company details     | company        |
| POST   | /posts                            | Post an internship (201)   | company        |
| GET    | /posts                            | List own posts             | company        |
| PATCH  | /posts/{post_id}                  | Update / close a post      | company        |
| GET    | /posts/{post_id}/applicants       | View applicants            | company        |
| PATCH  | /applications/{application_id}/status | Advance/reject applicant | company    |

### Admin (`/admin`)

| Method | Path         | Description                              | Auth  |
| ------ | ------------ | ---------------------------------------- | ----- |
| GET    | /users       | List all users                           | admin |
| GET    | /posts       | List all posts                           | admin |
| GET    | /applications | Overview all applications               | admin |
| DELETE | /posts/{post_id} | Remove a post (cascades applications) | admin |
| DELETE | /users/{user_id} | Remove a user (self-delete blocked)  | admin |

Swagger UI is auto-generated by FastAPI at `/docs` (needs no extra setup).

## Architecture

React (Vite) client -> FastAPI routers -> service layer -> SQLAlchemy models -> PostgreSQL (SQLite fallback for local dev). Auth and config live in `app/core/`. CI runs backend and frontend pipelines on every push/PR to `main`.

![System architecture](docs/diagrams/architecture.png)

Module breakdown: `docs/diagrams/module-diagram.md` - API reference: `docs/diagrams/api-contract.md`

## DB Design

8 tables: `users`, `student_profiles`, `companies`, `skills`, `student_skills`, `internship_posts`, `post_skills`, `applications`. Guards that matter: `UNIQUE(student_id, post_id)` (no double-apply), `UNIQUE(skill.name)` (case-insensitive match), `role`/`status` enums, SQLite dev / PostgreSQL 15 prod (CI runs the suite against Postgres).

![ER diagram](docs/diagrams/er-diagram.png)

Full schema notes: `docs/db-schema.md`

## Core / Auth

- `app/core/config.py` - single `Settings` object (env-driven); refuses to boot in production with the placeholder `SECRET_KEY`.
- `app/core/security.py` - bcrypt password hashing (configurable rounds) + HS256 JWT access tokens (60 min default).
- `app/core/deps.py` - `get_current_user` (401 on missing/expired/forged token, rejects non-integer `sub`) + `require_roles` guards (403 on wrong role, 404 on cross-tenant access).

Source files for all diagrams live in `docs/diagrams/`.

## Folder Structure

```
.
├── app/
│   ├── api/          # routers
│   ├── core/         # config, security
│   ├── db/           # engine + session
│   └── models/       # SQLAlchemy models
├── frontend/
│   └── src/          # React app (Vite)
├── docs/
│   ├── db-schema.md
│   ├── domain-study.md
│   └── diagrams/     # architecture, ER, module (.md + rendered .png)
├── tests/
├── .github/workflows/
├── Problem_Statement.md
├── requirements.txt
└── README.md
```

## Deployment / CI/CD

Two GitHub Actions pipelines run on every push/PR to `main`: `backend.yml` (black + flake8 + pytest with `--cov-fail-under=85` against a Postgres 15 service, then Render deploy hook on `main` pushes via `RENDER_DEPLOY_HOOK_URL` secret) and `frontend.yml` (`npm ci` + `npm run build`, then Vercel deploy on `main` pushes via `VERCEL_TOKEN`/`VERCEL_ORG_ID`/`VERCEL_PROJECT_ID` secrets). Deploy the backend from `render.yaml` on Render and the frontend (`frontend/` root) on Vercel with `VITE_API_URL` pointed at the Render URL.

## Future Enhancements

- AI resume / skill-matching scoring (Day 42–59 enhancement)
- Company review/approval flow for company accounts
- Refresh-token rotation and login rate limiting

## License

MIT — see [LICENSE](LICENSE).

## Author

Aashik Ahmed (aashikahamed029@gmail.com) — see [LICENSE](LICENSE).

## Team & Contributions

| Member | Role | Contribution |
| ------ | ---- | ------------ |
| Aashik Ahmed | Solo developer (Python batch) | Backend, frontend, CI/CD, docs — 100% |

## Test Report

- Suite: `pytest tests` — 48 tests passing (auth, students, companies, admin incl. overview + manage deletes, email).
- Coverage: 95% overall (`pytest --cov=app`), gate `--cov-fail-under=85` enforced in CI.
- CI: backend job runs black + flake8 + pytest with coverage against Postgres 15 then triggers Render deploy hook; frontend job runs `npm ci` + `npm run build` then deploys to Vercel.

## Hosting

- Backend: Render web service from `render.yaml` (Python 3.12, Postgres 15, `uvicorn app.main:app`). Health: `/api/v1/health`.
- Frontend: Vercel static deploy, project root `frontend/`, SPA fallback in `frontend/vercel.json`, backend URL via `VITE_API_URL`.
- Live URLs: _added after first deploy_.

## Demo

- Demo video: _link added after recording_.
- Local demo: `uvicorn app.main:app --reload` + `cd frontend && npm run dev`; Swagger at `http://localhost:8000/docs`.
