"""Admin routes: platform-wide management (role: admin)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.base import get_db
from app.models import User
from app.services import admin as admin_service

router = APIRouter(prefix="/admin", tags=["admin"])
admin_guard = require_roles("admin")


@router.get("/users")
def list_users(db: Session = Depends(get_db), user: User = Depends(admin_guard)):
    """List every user (students, companies, admins)."""
    users = admin_service.list_users(db)
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "created_at": u.created_at,
        }
        for u in users
    ]


@router.get("/posts")
def list_all_posts(db: Session = Depends(get_db), user: User = Depends(admin_guard)):
    """List every internship post on the platform."""
    posts = admin_service.list_posts(db)
    return [
        {
            "id": p.id,
            "company_id": p.company_id,
            "title": p.title,
            "is_open": p.is_open,
            "posted_at": p.posted_at,
        }
        for p in posts
    ]


@router.get("/applications")
def list_all_applications(
    db: Session = Depends(get_db), user: User = Depends(admin_guard)
):
    """Overview all applications with student and post context."""
    return admin_service.list_applications(db)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int, db: Session = Depends(get_db), user: User = Depends(admin_guard)
):
    """Remove an inappropriate post (cascades its applications)."""
    admin_service.delete_post(db, post_id)
    return None


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, db: Session = Depends(get_db), user: User = Depends(admin_guard)
):
    """Remove a user and their profile/posts via cascades."""
    admin_service.delete_user(db, user_id, current_admin_id=user.id)
    return None
