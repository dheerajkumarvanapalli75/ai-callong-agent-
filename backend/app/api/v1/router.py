from fastapi import APIRouter
from app.api.v1 import audit, auth, businesses

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router)
api_v1_router.include_router(businesses.router)
api_v1_router.include_router(audit.router)
