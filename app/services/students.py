from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import (
    Application,
    InternshipPost,
    PostSkill,
    Skill,
    StudentProfile,
    StudentSkill,
    User,
)


def get_profile(db: Session, user: User) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found"
        )
    return profile


def update_profile(db: Session, user: User, payload) -> StudentProfile:
    profile = get_profile(db, user)
    for field in ("bio", "education", "resume_url", "phone"):
        value = getattr(payload, field, None)
        if value is not None:
            setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


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


def add_skill(db: Session, user: User, name: str) -> Skill:
    profile = get_profile(db, user)
    skill = _get_or_create_skill(db, name)
    exists = (
        db.query(StudentSkill)
        .filter(
            StudentSkill.student_id == profile.id, StudentSkill.skill_id == skill.id
        )
        .first()
    )
    if exists is None:
        db.add(StudentSkill(student_id=profile.id, skill_id=skill.id))
        db.commit()
    return skill


def list_skills(db: Session, user: User) -> list[Skill]:
    profile = get_profile(db, user)
    rows = (
        db.query(Skill)
        .join(StudentSkill, StudentSkill.skill_id == Skill.id)
        .filter(StudentSkill.student_id == profile.id)
        .all()
    )
    return rows


def list_posts(
    db: Session,
    query: str = "",
    location: str = "",
    skill: str = "",
) -> list[InternshipPost]:
    def _like(value: str) -> str:
        escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        return f"%{escaped}%"

    stmt = db.query(InternshipPost).filter(InternshipPost.is_open.is_(True))

    if query:
        stmt = stmt.filter(InternshipPost.title.ilike(_like(query), escape="\\"))
    if location:
        stmt = stmt.filter(InternshipPost.location.ilike(_like(location), escape="\\"))
    if skill:
        stmt = (
            stmt.join(PostSkill, PostSkill.post_id == InternshipPost.id)
            .join(Skill, Skill.id == PostSkill.skill_id)
            .filter(Skill.name.ilike(_like(skill), escape="\\"))
            .distinct()
        )
    return stmt.order_by(InternshipPost.posted_at.desc()).all()


def apply(db: Session, user: User, post_id: int, cover_note: str) -> Application:
    profile = get_profile(db, user)
    post = db.get(InternshipPost, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Internship post not found"
        )
    if not post.is_open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This internship is closed"
        )

    existing = (
        db.query(Application)
        .filter(Application.student_id == profile.id, Application.post_id == post_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already applied to this internship",
        )

    application = Application(
        student_id=profile.id, post_id=post_id, cover_note=cover_note
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def list_applications(db: Session, user: User) -> list[Application]:
    profile = get_profile(db, user)
    return (
        db.query(Application)
        .filter(Application.student_id == profile.id)
        .order_by(Application.applied_at.desc())
        .all()
    )
