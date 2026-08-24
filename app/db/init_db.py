from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base, SessionLocal, engine
from app.models import User


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        return

    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if existing is None:
            db.add(
                User(
                    email=settings.ADMIN_EMAIL,
                    password_hash=hash_password(settings.ADMIN_PASSWORD),
                    full_name=settings.ADMIN_NAME,
                    role="admin",
                )
            )
            db.commit()
    finally:
        db.close()
