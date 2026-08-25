from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.base import get_db
from app.models import User
from app.schemas.company import (
    ApplicantOut,
    CompanyOut,
    CompanyProfileUpdate,
    PostIn,
    PostUpdate,
    StatusIn,
)
from app.services import companies as company_service

router = APIRouter(prefix="/companies", tags=["companies"])
company_guard = require_roles("company")


@router.get("/profile", response_model=CompanyOut)
def get_profile(db: Session = Depends(get_db), user: User = Depends(company_guard)):
    return company_service.get_company(db, user)


@router.patch("/profile", response_model=CompanyOut)
def update_profile(
    payload: CompanyProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(company_guard),
):
    return company_service.update_company(db, user, payload)


@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostIn, db: Session = Depends(get_db), user: User = Depends(company_guard)
):
    return _post_payload(company_service.create_post(db, user, payload))


@router.get("/posts")
def list_posts(db: Session = Depends(get_db), user: User = Depends(company_guard)):
    return [_post_payload(p) for p in company_service.list_posts(db, user)]


@router.patch("/posts/{post_id}")
def update_post(
    post_id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(company_guard),
):
    return _post_payload(company_service.update_post(db, user, post_id, payload))


@router.get("/posts/{post_id}/applicants", response_model=list[ApplicantOut])
def list_applicants(
    post_id: int, db: Session = Depends(get_db), user: User = Depends(company_guard)
):
    return company_service.list_applicants(db, user, post_id)


@router.patch("/applications/{application_id}/status")
def update_status(
    application_id: int,
    payload: StatusIn,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(company_guard),
):
    application = company_service.update_status(
        db, user, application_id, payload.status, background
    )
    return {
        "id": application.id,
        "post_id": application.post_id,
        "student_id": application.student_id,
        "status": application.status,
        "updated_at": application.updated_at,
    }


def _post_payload(post):
    return {
        "id": post.id,
        "company_id": post.company_id,
        "company_name": post.company.name if post.company else "",
        "title": post.title,
        "description": post.description,
        "location": post.location,
        "internship_type": post.internship_type,
        "duration": post.duration,
        "stipend": post.stipend,
        "is_open": post.is_open,
        "posted_at": post.posted_at,
        "skills": [s.skill.name for s in post.post_skills],
    }
