# app/coffeeshop/api/health.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import time
from ..infrastructure.database import get_db_session

router = APIRouter()


@router.get("")
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "coffetime-api"
    }


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db_session)):
    """Detailed health check with database connectivity"""

    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "coffetime-api",
        "checks": {}
    }

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"

    # Check disk space
    import shutil
    try:
        disk_usage = shutil.disk_usage("/")
        free_space_gb = disk_usage.free / (1024**3)

        if free_space_gb > 1:  # More than 1GB free space
            health_status["checks"]["disk"] = {
                "status": "healthy",
                "free_space_gb": round(free_space_gb, 2)
            }
        else:
            health_status["checks"]["disk"] = {
                "status": "warning",
                "free_space_gb": round(free_space_gb, 2)
            }
    except Exception as e:
        health_status["checks"]["disk"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Return appropriate status
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status
