from fastapi import APIRouter

from app.api.v1.endpoints.access import router as access_router
from app.api.v1.endpoints.details import router as details_router
from app.api.v1.endpoints.users import router as users_router

api_router = APIRouter(prefix="/v1/api")
api_router.include_router(users_router)
api_router.include_router(access_router)
api_router.include_router(details_router)
