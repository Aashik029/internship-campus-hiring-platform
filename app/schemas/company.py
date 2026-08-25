from pydantic import BaseModel, ConfigDict, Field, field_validator


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    industry: str = ""
    website: str = ""
    description: str = ""
    location: str = ""


class CompanyProfileUpdate(BaseModel):
    name: str | None = None
    industry: str | None = None
    website: str | None = None
    description: str | None = None
    location: str | None = None


class PostOut(BaseModel):
    id: int
    company_id: int
    company_name: str = ""
    title: str
    description: str
    location: str = ""
    internship_type: str = ""
    duration: str = ""
    stipend: str = ""
    is_open: bool = True
    posted_at: object | None = None
    skills: list[str] = []


class PostIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=5000)
    location: str = Field(default="", max_length=255)
    internship_type: str = Field(default="", max_length=100)
    duration: str = Field(default="", max_length=100)
    stipend: str = Field(default="", max_length=100)
    skills: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("skills")
    @classmethod
    def _clean_skill_names(cls, value: list[str]) -> list[str]:
        cleaned = [v.strip() for v in value if v and v.strip()]
        if len(cleaned) != len(value):
            raise ValueError("Skill names must be non-empty")
        for name in cleaned:
            if len(name) > 100:
                raise ValueError("Skill names must be at most 100 characters")
        return cleaned


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1, max_length=5000)
    location: str | None = Field(default=None, max_length=255)
    is_open: bool | None = None

    @field_validator("title", "description", "location", mode="before")
    @classmethod
    def _empty_to_none(cls, value):
        # PATCH semantics: empty string means "no change".
        if value == "":
            return None
        return value


class StatusIn(BaseModel):
    status: str = Field(pattern="^(applied|shortlisted|interview|selected|rejected)$")


class ApplicantOut(BaseModel):
    id: int
    student_id: int
    student_name: str = ""
    email: str = ""
    status: str
    cover_note: str = ""
    applied_at: object | None = None
    skills: list[str] = []
