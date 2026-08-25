import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import Company, StudentProfile, User

logger = logging.getLogger(__name__)


def register_user(
    db: Session, email: str, password: str, full_name: str, role: str
) -> User:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        logger.warning("Signup rejected: email already registered email=%s", email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role,
    )
    db.add(user)
    db.flush()

    if role == "student":
        db.add(StudentProfile(user_id=user.id))
    elif role == "company":
        db.add(Company(user_id=user.id, name=full_name))

    db.commit()
    db.refresh(user)
    logger.info("User registered email=%s role=%s", email, role)
    return user


def authenticate(db: Session, email: str, password: str) -> str:
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(password, user.password_hash):
        logger.warning("Failed login attempt email=%s", email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    logger.info("User logged in email=%s role=%s", email, user.role)
    return create_access_token(subject=str(user.id))
