import logging

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from app.models import (
    Application,
    Company,
    InternshipPost,
    PostSkill,
    Skill,
    StudentProfile,
    User,
)
from app.services.email import notify_status_change

logger = logging.getLogger(__name__)


def get_company(db: Session, user: User) -> Company:
    company = db.query(Company).filter(Company.user_id == user.id).first()
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found"
        )
    return company


def update_company(db: Session, user: User, payload) -> Company:
    company = get_company(db, user)
    for field in ("name", "industry", "website", "description", "location"):
        value = getattr(payload, field, None)
        if value is not None:
            setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return company


def _normalize_skill_name(name: str) -> str:
    return " ".join(name.strip().split())


def _get_or_create_skill(db: Session, name: str) -> Skill:
    cleaned = _normalize_skill_name(name)
    skill = db.query(Skill).filter(Skill.name.ilike(cleaned)).first()
    if skill is None:
        skill = Skill(name=cleaned)
        db.add(skill)
        db.flush()
    return skill


def create_post(db: Session, user: User, payload) -> InternshipPost:
    company = get_company(db, user)
    post = InternshipPost(
        company_id=company.id,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        internship_type=payload.internship_type,
        duration=payload.duration,
        stipend=payload.stipend,
    )
    db.add(post)
    db.flush()

    for name in payload.skills:
        skill = _get_or_create_skill(db, name)
        db.add(PostSkill(post_id=post.id, skill_id=skill.id))

    db.commit()
    db.refresh(post)
    return post


def list_posts(db: Session, user: User) -> list[InternshipPost]:
    company = get_company(db, user)
    return (
        db.query(InternshipPost)
        .filter(InternshipPost.company_id == company.id)
        .order_by(InternshipPost.posted_at.desc())
        .all()
    )


def update_post(db: Session, user: User, post_id: int, payload) -> InternshipPost:
    company = get_company(db, user)
    post = db.get(InternshipPost, post_id)
    if post is None or post.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Internship post not found"
        )

    for field in ("title", "description", "location", "is_open"):
        value = getattr(payload, field, None)
        if value is not None:
            setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post


def list_applicants(db: Session, user: User, post_id: int) -> list[dict]:
    company = get_company(db, user)
    post = db.get(InternshipPost, post_id)
    if post is None or post.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Internship post not found"
        )

    rows = (
        db.query(Application, StudentProfile, User)
        .join(StudentProfile, Application.student_id == StudentProfile.id)
        .join(User, StudentProfile.user_id == User.id)
        .filter(Application.post_id == post_id)
        .all()
    )

    applicants = []
    for application, profile, student_user in rows:
        skills = [link.skill.name for link in profile.skills]
        applicants.append(
            {
                "id": application.id,
                "student_id": profile.id,
                "student_name": student_user.full_name,
                "email": student_user.email,
                "status": application.status,
                "cover_note": application.cover_note,
                "applied_at": application.applied_at,
                "skills": skills,
            }
        )
    return applicants


def _safe_notify(**kwargs) -> None:
    """Send a status-change email without ever breaking the request."""
    try:
        notify_status_change(**kwargs)
    except Exception:  # noqa: BLE001 — email must never break the API
        logger.warning("Status-change email failed", exc_info=True)


def update_status(
    db: Session,
    user: User,
    application_id: int,
    new_status: str,
    background: BackgroundTasks | None = None,
) -> Application:
    company = get_company(db, user)
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    post = db.get(InternshipPost, application.post_id)
    if post is None or post.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your application"
        )

    application.status = new_status
    db.commit()
    db.refresh(application)

    profile = db.get(StudentProfile, application.student_id)
    student_user = db.get(User, profile.user_id) if profile else None
    if student_user and post.title:
        notify_kwargs = {
            "student_email": student_user.email,
            "student_name": student_user.full_name,
            "post_title": post.title,
            "company_name": company.name,
            "new_status": new_status,
        }
        if background is not None:
            # Send after the response: SMTP latency never blocks the API.
            background.add_task(_safe_notify, **notify_kwargs)
        else:
            _safe_notify(**notify_kwargs)

    return application
