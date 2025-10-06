# app/coffeeshop/api/catalog.py
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from ..infrastructure.database import get_db_session
from ..services.product_service import ProductService
from ..services.category_service import CategoryService
from ..api.dependencies import get_product_service, get_category_service

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/coffeeshop/templates")


@router.get("/catalog/products", response_class=HTMLResponse)
async def get_products(
    request: Request,
    category: Optional[str] = None,
    q: Optional[str] = None,
    product_service: ProductService = Depends(get_product_service)
):
    try:
        if q and q.strip():
            products = await product_service.search_products(q.strip())
        elif category and category != "All":
            products = await product_service.get_products_by_category(category)
        else:
            products = await product_service.get_active_products()

        if not products:
            return HTMLResponse("""
            <div class="text-center py-12">
                <div class="w-24 h-24 mx-auto mb-4 bg-coffee-gray rounded-full flex items-center justify-center">
                    <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                </div>
                <p class="text-gray-500">No products available</p>
            </div>
            """)

        return templates.TemplateResponse(
            "partials/product_list.html",
            {
                "request": request,
                "products": products,
                "search_query": q
            }
        )

    except Exception as e:
        return HTMLResponse(f"""
        <div class="text-center py-12">
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Error loading products</h3>
            <p class="text-gray-600">{str(e)}</p>
        </div>
        """)


@router.get("/catalog/categories", response_class=HTMLResponse)
async def get_categories(
    request: Request,
    category_service: CategoryService = Depends(get_category_service)
):
    try:
        categories = await category_service.get_active_categories()

        all_categories = [{"name": "All", "slug": "all"}] + [
            {"name": cat.name, "slug": cat.slug} for cat in categories
        ]

        return templates.TemplateResponse(
            "partials/category_filters.html",
            {
                "request": request,
                "categories": all_categories
            }
        )

    except Exception as e:
        return HTMLResponse(f'<div class="text-red-500">Error loading categories: {str(e)}</div>')


@router.get("/catalog/category/{category_slug}", response_class=HTMLResponse)
async def get_products_by_category_slug(
    category_slug: str,
    request: Request,
    product_service: ProductService = Depends(get_product_service)
):
    try:
        if category_slug == "all":
            products = await product_service.get_active_products()
        else:
            products = await product_service.get_products_by_category_slug(category_slug)

        return templates.TemplateResponse(
            "partials/product_list.html",
            {
                "request": request,
                "products": products
            }
        )

    except Exception as e:
        return HTMLResponse(f'<div class="text-red-500">Error: {str(e)}</div>')


@router.get("/catalog/search", response_class=HTMLResponse)
async def search_products(
    request: Request,
    q: str = "",
    product_service: ProductService = Depends(get_product_service)
):
    try:
        if q.strip():
            products = await product_service.search_products(q)
        else:
            products = await product_service.get_active_products()

        return templates.TemplateResponse(
            "partials/product_list.html",
            {
                "request": request,
                "products": products,
                "search_query": q
            }
        )

    except Exception as e:
        return HTMLResponse(f'<div class="text-red-500">Error: {str(e)}</div>')

@router.get("/product/{product_id}", response_class=HTMLResponse)
async def get_product_detail(
    product_id: int,
    request: Request,
    product_service: ProductService = Depends(get_product_service)
):
    try:
        product = await product_service.get_product_by_id(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return templates.TemplateResponse(
            "product_detail.html",
            {
                "request": request,
                "product": product
            }
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
