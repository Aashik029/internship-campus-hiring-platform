# Database Schema — v1 (Week 1)

8 tables. Primary keys are `id` everywhere unless noted.
Status columns use enum values. All timestamps are UTC.

## Table map

```
users ──1:1── student_profiles ──M:N── skills (via student_skills)
users ──1:1── companies ──1:M── internship_posts ──M:N── skills (via post_skills)
student_profiles ──M:N── internship_posts (via applications, with status)
```

## users
- `id` PK
- `email` UNIQUE, NOT NULL
- `password_hash` NOT NULL
- `role` enum(student | company | admin), NOT NULL
- `full_name` NOT NULL
- `created_at` timestamp

## student_profiles (1:1 with users)
- `id` PK
- `user_id` FK → users.id, UNIQUE
- `bio`, `education`, `resume_url`, `phone`

## companies (1:1 with users)
- `id` PK
- `user_id` FK → users.id, UNIQUE
- `name` NOT NULL, `industry`, `website`, `description`, `location`

## skills
- `id` PK
- `name` UNIQUE, NOT NULL

## internship_posts (M:1 with companies)
- `id` PK
- `company_id` FK → companies.id, NOT NULL
- `title` NOT NULL, `description` NOT NULL, `location`, `internship_type`, `duration`, `stipend`
- `is_open` bool default true
- `posted_at` timestamp

## post_skills (junction: internship_post ↔ skill)
- `post_id` FK → internship_posts.id (PK part)
- `skill_id` FK → skills.id (PK part)

## student_skills (junction: student_profile ↔ skill)
- `student_id` FK → student_profiles.id (PK part)
- `skill_id` FK → skills.id (PK part)

## applications (core business table: student ↔ post, with status)
- `id` PK
- `student_id` FK → student_profiles.id, NOT NULL
- `post_id` FK → internship_posts.id, NOT NULL
- `status` enum(applied | shortlisted | interview | selected | rejected), default `applied`
- `cover_note` text
- `applied_at`, `updated_at` timestamps
- UNIQUE(student_id, post_id) — one application per student per post