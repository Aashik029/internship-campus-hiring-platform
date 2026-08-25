from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.base import get_db
from app.models import User
from app.schemas.student import (
    ApplicationIn,
    ApplicationOut,
    ProfileOut,
    SkillIn,
    SkillOut,
    StudentProfileUpdate,
)
from app.services import students as student_service

router = APIRouter(prefix="/students", tags=["students"])
student_guard = require_roles("student")


@router.get("/profile", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db), user: User = Depends(student_guard)):
    return student_service.get_profile(db, user)


@router.patch("/profile", response_model=ProfileOut)
def update_profile(
    payload: StudentProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(student_guard),
):
    return student_service.update_profile(db, user, payload)


@router.get("/skills", response_model=list[SkillOut])
def get_skills(db: Session = Depends(get_db), user: User = Depends(student_guard)):
    return student_service.list_skills(db, user)


@router.post("/skills", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
def add_skill(
    payload: SkillIn, db: Session = Depends(get_db), user: User = Depends(student_guard)
):
    return student_service.add_skill(db, user, payload.name)


@router.get("/posts")
def list_posts(
    query: str = Query("", description="Search by title", max_length=100),
    location: str = Query("", max_length=100),
    skill: str = Query("", max_length=100),
    db: Session = Depends(get_db),
    user: User = Depends(student_guard),
):
    posts = student_service.list_posts(db, query, location, skill)
    return [
        {
            "id": p.id,
            "company_id": p.company_id,
            "company_name": p.company.name if p.company else "",
            "title": p.title,
            "description": p.description,
            "location": p.location,
            "internship_type": p.internship_type,
            "duration": p.duration,
            "stipend": p.stipend,
            "is_open": p.is_open,
            "posted_at": p.posted_at,
            "skills": [s.skill.name for s in p.post_skills],
        }
        for p in posts
    ]


@router.post(
    "/applications", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED
)
def apply(
    payload: ApplicationIn,
    db: Session = Depends(get_db),
    user: User = Depends(student_guard),
):
    application = student_service.apply(db, user, payload.post_id, payload.cover_note)
    return _application_payload(db, application)


@router.get("/applications", response_model=list[ApplicationOut])
def my_applications(db: Session = Depends(get_db), user: User = Depends(student_guard)):
    applications = student_service.list_applications(db, user)
    return [_application_payload(db, a) for a in applications]


def _application_payload(db, application):
    return {
        "id": application.id,
        "student_id": application.student_id,
        "post_id": application.post_id,
        "post_title": application.post.title if application.post else "",
        "company_name": (
            application.post.company.name
            if application.post and application.post.company
            else ""
        ),
        "status": application.status,
        "cover_note": application.cover_note,
        "applied_at": application.applied_at,
        "updated_at": application.updated_at,
    }
