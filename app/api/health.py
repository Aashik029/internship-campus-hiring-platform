from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/")
def root() -> dict:
    return {"message": "Internship & Campus Hiring Platform API", "version": "0.1.0"}