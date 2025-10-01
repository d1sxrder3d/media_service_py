from src.app.api.v1.jobs import router as v1_jobs_router
from src.app.api.v1.process import router as v1_process_router

from fastapi import APIRouter

main_router = APIRouter()

main_router.include_router(v1_jobs_router, prefix="/v1")
main_router.include_router(v1_process_router, prefix="/v1")
