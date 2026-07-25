from fastapi import APIRouter
from app.api.v1.endpoints import analytics,auth

api_router = APIRouter()

# Register analytics endpoints with a prefix and tags for OpenAPI docs
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Market Analytics"])