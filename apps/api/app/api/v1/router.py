"""API v1 router aggregating all endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import analysis, interviewers, jobs, login, uploads

api_router = APIRouter()

api_router.include_router(login.router, tags=["auth"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(interviewers.router, prefix="/interviewers", tags=["interviewers"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
