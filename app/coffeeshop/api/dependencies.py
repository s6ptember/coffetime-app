# app/coffeeshop/api/dependencies.py - Обновленная версия
from fastapi import Depends, Request, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.database import get_db_session
from ..services.product_service import ProductService
from ..services.category_service import CategoryService
from ..services.session_cart_service import SessionCartService  # Новый импорт


async def get_product_service(db: AsyncSession = Depends(get_db_session)) -> ProductService:
    """Dependency to get product service"""
    return ProductService(db)


async def get_category_service(db: AsyncSession = Depends(get_db_session)) -> CategoryService:
    """Dependency to get category service"""
    return CategoryService(db)


async def get_session_cart_service(db: AsyncSession = Depends(get_db_session)) -> SessionCartService:
    """Dependency to get session cart service"""
    return SessionCartService(db)


async def get_order_service(db: AsyncSession = Depends(get_db_session)):
    """Dependency to get order service"""
    from ..services.order_service import OrderService
    return OrderService(db)


async def get_admin_service(db: AsyncSession = Depends(get_db_session)):
    """Dependency to get admin service"""
    from ..services.admin_service import AdminService
    return AdminService(db)
