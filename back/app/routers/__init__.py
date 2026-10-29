from fastapi import APIRouter

from app.routers import admin, auth, mobile

api_router = APIRouter(prefix='/api')
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(mobile.router)
