# Domain Study — Week 1

## Project: Internship & Campus Hiring Platform

### Business Overview

The platform connects two primary user groups:
1. **Students** — seeking internship opportunities
2. **Companies** — looking to hire intern-level talent

An **Admin** oversees the platform as a third role.

### Key Business Rules

1. **Authentication**: Every user (regardless of role) has a single account
   in the `users` table. The `role` column determines what they can access.

2. **Profile separation**: Students and companies each have a 1:1 profile
   linked to their user record. A user can only have one type of profile.

3. **Application lifecycle**: An application moves through 5 statuses:
   `applied → shortlisted → interview → selected → rejected`.
   Company users drive status transitions; students can only view their own.

4. **Skills matching**: Both internship posts and student profiles attach
   skills via many-to-many junction tables. A post requires skills; a
   student claims skills they possess.

### Entity Relationships

```
users (1) ──(1:1)──▶ student_profiles (M:N) ──▶ skills
  │                                 ▲
  └──(1:1)──▶ companies (1:M) ──▶ internship_posts (M:N) ──▶ skills
                                              │
                                              ▼
                                student_profiles (M:N) ──▶ internship_posts
                                                               via applications
```

### User Workflows

**Student flow:**
1. Register → auto-creates student_profile
2. Build profile (bio, education, phone, resume)
3. Add skills
4. Browse/search internship posts by location or skill
5. Apply to a post (one application per post max)
6. View dashboard with current application statuses

**Company flow:**
1. Register → auto-creates company profile
2. Complete company profile (name, industry, website, location)
3. Post an internship with required skills
4. View applicants for own posts
5. Move applications through the status pipeline

**Admin flow:**
1. Manage all users (students, companies)
2. Manage internship posts (view, remove if inappropriate)
3. Oversee all applications

### Third-Party Integration Points

- **Email** (Phase 2): Notify students on status change, notify companies of new applications
- **SMS** (Phase 3): Optional interview reminders
- **Maps** (Phase 3): Geocode company location fields
- **Payment** (Phase 6): Stipend disbursement (explicitly out of scope per Problem_Statement)

### AI Enhancement Opportunities

- Resume/skill extraction from uploaded documents (Day 42–59 enhancement)
- Semantic skill matching (beyond exact name match)
- Automated shortlisting based on skill overlap score

### Stack Decision Rationale

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.12 | Familiar, strong ecosystem for AI integration |
| Framework | FastAPI | Auto-generated OpenAPI docs, async support, type safety |
| ORM | SQLAlchemy 2.0 | Mature, supports both SQLite (local) and PostgreSQL (prod) |
| Auth | JWT (python-jose) + bcrypt (passlib) | Stateless, scalable, industry standard |
| Database | SQLite → PostgreSQL | SQLite for zero-setup dev; PostgreSQL for production |
| Testing | pytest | Python standard, integrates with FastAPI TestClient |
| CI/CD | GitHub Actions | Already integrated with GitHub, no extra service needed |
| Frontend | React + Tailwind (Week 3) | Component-based, matches FastAPI REST contract |

### Schema Design Notes

- 8 tables (see `docs/db-schema.md`)
- All timestamps in UTC
- UUIDs deferred to keep scaffold simple (integer PKs)
- Enum columns for role and status (type safety at DB level)
