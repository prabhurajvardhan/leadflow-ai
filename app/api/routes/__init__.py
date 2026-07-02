from fastapi import APIRouter
from app.api.routes import auth, workspaces, leads, jobs

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(workspaces.router)
api_router.include_router(leads.router)
api_router.include_router(jobs.router)
