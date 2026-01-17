"""API v1 router aggregating all endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import login, uploads

api_router = APIRouter()

api_router.include_router(login.router, tags=["auth"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
