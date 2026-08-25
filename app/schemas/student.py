from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    bio: str = ""
    education: str = ""
    resume_url: str = ""
    phone: str = ""


class StudentProfileUpdate(BaseModel):
    bio: str | None = Field(default=None, max_length=2000)
    education: str | None = Field(default=None, max_length=500)
    resume_url: str | None = Field(default=None, max_length=2048)
    phone: str | None = Field(default=None, max_length=32)


class SkillOut(BaseModel):
    id: int
    name: str


class SkillIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Skill name must be non-empty")
        return cleaned


class ApplicationIn(BaseModel):
    post_id: int = Field(gt=0)
    cover_note: str = Field(default="", max_length=2000)


class ApplicationOut(BaseModel):
    id: int
    student_id: int
    post_id: int
    post_title: str = ""
    company_name: str = ""
    status: str
    cover_note: str = ""
    applied_at: object | None = None
    updated_at: object | None = None
