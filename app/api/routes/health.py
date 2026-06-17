from fastapi import APIRouter
import os
import time
from app.core.config import Config
router = APIRouter()

START_TIME = time.time()


@router.get("/")
def health_check():
    """
    Basic health check endpoint
    """

    return {
        "status": "ok",
        "service": Config.SERVICE_NAME,
        "uptime_seconds": round(time.time() - START_TIME, 2)
    }


@router.get("/detailed")
def detailed_health():
    """
    More detailed system health info
    """

    return {
        "status": "ok",
        "service": Config.SERVICE_NAME,
        "environment":  Config.ENV,
        "uptime_seconds": round(time.time() - START_TIME, 2)
    }