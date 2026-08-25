from fastapi import APIRouter

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.companies import router as companies_router
from app.api.health import router as health_router
from app.api.students import router as students_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(students_router)
api_router.include_router(companies_router)
api_router.include_router(admin_router)
