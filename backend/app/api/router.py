from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.academics import router as academics_router
from app.api.v1.finance import router as finance_router
from app.api.v1.life_admin import router as life_admin_router
from app.api.v1.ai_chat import router as ai_chat_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(dashboard_router)
api_router.include_router(academics_router)
api_router.include_router(finance_router)
api_router.include_router(life_admin_router)
api_router.include_router(ai_chat_router)
