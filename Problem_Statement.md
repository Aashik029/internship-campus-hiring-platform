# Problem Statement

## 1. Title
Internship & Campus Hiring Platform

## 2. Domain
HRTech / EdTech — campus placement and internship recruitment

## 3. Who is the user? (2-3 user types, with roles)
1. **Student** — a learner seeking an internship. Creates a profile, adds skills, browses/searches internship posts, applies, and tracks the status of every application (Applied → Shortlisted → Interview → Selected).
2. **Company** — a recruiter wanting interns. Registers, builds a company profile, posts internship opportunities with required skills, views students who applied, and manages/updates application statuses.
3. **Admin** — platform operator. Manages students, companies, internship posts, applications, and overall platform access.

## 4. What problem are we solving? (3-5 sentences, real-life example)
Students looking for internships must chase postings across many portals, keep manual notes on what they applied to, and have no single place to see whether a company shortlisted them or not. Companies receive dozens of applications per post and end up sorting through emails and spreadsheets to find suitable candidates.

Example: Aashik knows Python, React, and SQL. He finds a "Python Developer Intern" post on the platform, applies in one step, and can later check whether the application is **Applied**, **Shortlisted**, **Interview**, or **Selected** — without emailing anyone.

## 5. Proposed Solution (what the application will do, feature-wise)
- **Student module**: register/login, create and edit a profile, add skills, view available internships, search/filter internships, apply to a post, and see a live status board of all applications.
- **Company module**: register/login, create a company profile, post internship opportunities with required skills and details, view the list of applicants per post, and move a student's application through the status pipeline (Shortlist / Interview / Selected / Rejected).
- **Admin module**: manage students and companies, review and manage internship posts, overview all applications, and manage platform users/access.
- **Skills matching**: the platform matches required skills on a post against the student's skills so students can judge fit and companies can judge candidates.

## 6. Core Entities / Database Tables (minimum 5)
1. `users` — common auth record for all roles (email, password_hash, role, name)
2. `student_profiles` — student-specific data (1:1 with users)
3. `companies` — company-specific data (1:1 with users)
4. `internship_posts` — internship opportunities (M:1 with companies)
5. `skills` — normalized skill vocabulary
6. `post_skills` — junction: which skills an internship requires (M:N post ↔ skill)
7. `student_skills` — junction: which skills a student has (M:N student ↔ skill)
8. `applications` — the core business table: who applied where, and the application status (M:N student ↔ post, with status)

## 7. User Roles & Permissions (minimum 2 distinct roles)
- **Student**: register/login; manage own profile, own skills; view & search internships; apply; view only their own applications and statuses.
- **Company**: register/login; manage own company profile; post/edit/close own internships; view applicants for own posts only; update status of applications to own posts only.
- **Admin**: full manage permissions across students, companies, posts, and applications; role assignment.
- Auth: JWT (python-jose) with bcrypt-hashed passwords. Role-based access control on every protected endpoint.

## 8. Success Criteria
- A student can register, complete a profile, and apply to an internship in under ~2 minutes.
- A student can see the up-to-date status (Applied/Shortlisted/Interview/Selected) of an application on their dashboard.
- A company can post an internship and shortlist an applicant in a few clicks.
- Status transitions are reflected immediately for both parties.
- The application supports the "Python Developer Intern" example above end-to-end.

## 9. Out of Scope (clearly list what you will NOT build)
- Payments, stipend payouts, or invoicing.
- In-app messaging / chat between student and company (notifications via email instead).
- Resume parsing / AI resume scoring in the base product (natural AI enhancement scope for the Day 42–59 enhancement phase).
- Calendar/interview scheduling with external calendars.
- Mobile app (responsive web only).
- Multi-language/localization.

## 10. Chosen Track
Python (FastAPI) + SQLAlchemy ORM + PostgreSQL/MySQL database + React.js frontend (added in Week 3). Auth via JWT (python-jose) with bcrypt password hashing.