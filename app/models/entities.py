from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String(255), unique=True, nullable=False, index=True)
    password_hash = sa.Column(sa.String(255), nullable=False)
    role = sa.Column(
        sa.Enum("student", "company", "admin", name="user_role"), nullable=False
    )
    full_name = sa.Column(sa.String(255), nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    student_profile = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    company = relationship(
        "Company", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id"), unique=True, nullable=False
    )
    bio = sa.Column(sa.Text, default="")
    education = sa.Column(sa.String(255), default="")
    resume_url = sa.Column(sa.String(500), default="")
    phone = sa.Column(sa.String(50), default="")

    user = relationship("User", back_populates="student_profile")
    skills = relationship(
        "StudentSkill", back_populates="student", cascade="all, delete-orphan"
    )
    applications = relationship(
        "Application", back_populates="student", cascade="all, delete-orphan"
    )


class Company(Base):
    __tablename__ = "companies"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id"), unique=True, nullable=False
    )
    name = sa.Column(sa.String(255), nullable=False)
    industry = sa.Column(sa.String(100), default="")
    website = sa.Column(sa.String(255), default="")
    description = sa.Column(sa.Text, default="")
    location = sa.Column(sa.String(255), default="")

    user = relationship("User", back_populates="company")
    posts = relationship(
        "InternshipPost", back_populates="company", cascade="all, delete-orphan"
    )


class Skill(Base):
    __tablename__ = "skills"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), unique=True, nullable=False, index=True)

    post_skills = relationship(
        "PostSkill", back_populates="skill", cascade="all, delete-orphan"
    )
    student_skills = relationship(
        "StudentSkill", back_populates="skill", cascade="all, delete-orphan"
    )


class InternshipPost(Base):
    __tablename__ = "internship_posts"

    id = sa.Column(sa.Integer, primary_key=True)
    company_id = sa.Column(
        sa.Integer, sa.ForeignKey("companies.id"), nullable=False, index=True
    )
    title = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=False)
    location = sa.Column(sa.String(255), default="")
    internship_type = sa.Column(sa.String(100), default="")
    duration = sa.Column(sa.String(100), default="")
    stipend = sa.Column(sa.String(100), default="")
    is_open = sa.Column(sa.Boolean, default=True)
    posted_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    company = relationship("Company", back_populates="posts")
    post_skills = relationship(
        "PostSkill", back_populates="post", cascade="all, delete-orphan"
    )
    applications = relationship(
        "Application", back_populates="post", cascade="all, delete-orphan"
    )


class PostSkill(Base):
    __tablename__ = "post_skills"

    post_id = sa.Column(
        sa.Integer, sa.ForeignKey("internship_posts.id"), primary_key=True
    )
    skill_id = sa.Column(sa.Integer, sa.ForeignKey("skills.id"), primary_key=True)

    post = relationship("InternshipPost", back_populates="post_skills")
    skill = relationship("Skill", back_populates="post_skills")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    student_id = sa.Column(
        sa.Integer, sa.ForeignKey("student_profiles.id"), primary_key=True
    )
    skill_id = sa.Column(sa.Integer, sa.ForeignKey("skills.id"), primary_key=True)

    student = relationship("StudentProfile", back_populates="skills")
    skill = relationship("Skill", back_populates="student_skills")


class ApplicationStatus:
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    SELECTED = "selected"
    REJECTED = "rejected"

    ALL = (APPLIED, SHORTLISTED, INTERVIEW, SELECTED, REJECTED)


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        sa.UniqueConstraint(
            "student_id", "post_id", name="uq_application_student_post"
        ),
    )

    id = sa.Column(sa.Integer, primary_key=True)
    student_id = sa.Column(
        sa.Integer, sa.ForeignKey("student_profiles.id"), nullable=False, index=True
    )
    post_id = sa.Column(
        sa.Integer, sa.ForeignKey("internship_posts.id"), nullable=False, index=True
    )
    status = sa.Column(
        sa.Enum(*ApplicationStatus.ALL, name="application_status"),
        default=ApplicationStatus.APPLIED,
    )
    cover_note = sa.Column(sa.Text, default="")
    applied_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=utcnow
    )

    student = relationship("StudentProfile", back_populates="applications")
    post = relationship("InternshipPost", back_populates="applications")
