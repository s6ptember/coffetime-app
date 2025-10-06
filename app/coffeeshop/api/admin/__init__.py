# app/coffeeshop/api/admin/__init__.py
import os
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import secrets

from ...api.dependencies import get_order_service, get_admin_service

from .dashboard import router as dashboard_router
from .categories import router as categories_router
from .sizes import router as sizes_router
from .products import router as products_router
from .orders import router as orders_router

router = APIRouter()
templates = Jinja2Templates(directory="app/coffeeshop/templates")
security = HTTPBasic()

def verify_admin(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv("ADMIN_USERNAME", "admin")
    correct_password = os.getenv("ADMIN_PASSWORD", "admin123")

    is_correct_username = secrets.compare_digest(credentials.username, correct_username)
    is_correct_password = secrets.compare_digest(credentials.password, correct_password)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic realm=\"Admin Panel\""}
        )
    return credentials.username

router.include_router(dashboard_router, dependencies=[Depends(verify_admin)])
router.include_router(categories_router, prefix="/categories", dependencies=[Depends(verify_admin)])
router.include_router(sizes_router, prefix="/sizes", dependencies=[Depends(verify_admin)])
router.include_router(products_router, prefix="/products", dependencies=[Depends(verify_admin)])
router.include_router(orders_router, prefix="/orders", dependencies=[Depends(verify_admin)])
