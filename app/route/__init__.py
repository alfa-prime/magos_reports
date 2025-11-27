from fastapi import APIRouter

from .health import router as health_router
from .report import router as report_router

router = APIRouter()
router.include_router(health_router)
router.include_router(report_router)
