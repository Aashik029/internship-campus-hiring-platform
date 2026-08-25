"""Admin service: platform-wide management for Review-II.

Admins can list users/posts/applications and remove
inappropriate posts or users. All role checks happen in
``app.api.admin`` via ``require_roles("admin")``.
"""

import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Application, InternshipPost, StudentProfile, User

logger = logging.getLogger(__name__)


def list_users(db: Session) -> list[User]:
    """Return all users newest-first."""
    return db.query(User).order_by(User.created_at.desc()).all()


def list_posts(db: Session) -> list[InternshipPost]:
    """Return all internship posts newest-first."""
    return db.query(InternshipPost).order_by(InternshipPost.posted_at.desc()).all()


def list_applications(db: Session) -> list[dict]:
    """Return every application with student/post context.

    Args:
        db: Active SQLAlchemy session.

    Returns:
        List of dicts with application, student email, and post title.
    """
    rows = (
        db.query(Application, StudentProfile, User, InternshipPost)
        .join(StudentProfile, Application.student_id == StudentProfile.id)
        .join(User, StudentProfile.user_id == User.id)
        .join(InternshipPost, Application.post_id == InternshipPost.id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    out = []
    for app_row, _profile, user_row, post_row in rows:
        out.append(
            {
                "id": app_row.id,
                "student_id": app_row.student_id,
                "student_email": user_row.email,
                "post_id": app_row.post_id,
                "post_title": post_row.title,
                "status": app_row.status,
                "applied_at": app_row.applied_at,
                "updated_at": app_row.updated_at,
            }
        )
    return out


def delete_post(db: Session, post_id: int) -> None:
    """Delete an internship post (cascades applicants/skills).

    Raises:
        HTTPException: 404 if the post does not exist.
    """
    post = db.get(InternshipPost, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Internship post not found",
        )
    logger.info("Admin deleting post id=%s title=%s", post.id, post.title)
    db.delete(post)
    db.commit()


def delete_user(db: Session, user_id: int, current_admin_id: int) -> None:
    """Delete a user and their profile/posts via cascades.

    Admins cannot delete themselves.

    Raises:
        HTTPException: 400 on self-delete, 404 if user missing.
    """
    if user_id == current_admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins cannot delete themselves",
        )
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    logger.info("Admin deleting user id=%s email=%s", user.id, user.email)
    db.delete(user)
    db.commit()
