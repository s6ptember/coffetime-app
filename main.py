# main.py
import uvicorn
import json
import logging
from decimal import Decimal
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.coffeeshop.infrastructure.database import get_db_session, async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from config import settings
from app.coffeeshop.api import catalog, cart, orders, health
from app.coffeeshop.api.admin import router as admin_router
from app.coffeeshop.infrastructure.database import init_db
from app.coffeeshop.middleware.logging_middleware import logging_middleware
from app.coffeeshop.middleware.error_handler import http_error_handler, general_error_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('aiosqlite').setLevel(logging.WARNING)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Coffetime PWA",
    description="Coffee Shop Module with PWA capabilities",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(logging_middleware)

app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(RequestValidationError, http_error_handler)
app.add_exception_handler(Exception, general_error_handler)

app.mount("/static", StaticFiles(directory="app/coffeeshop/static"), name="static")

templates = Jinja2Templates(directory="app/coffeeshop/templates")

app.include_router(catalog.router, tags=["catalog"])
app.include_router(cart.router, prefix="/cart", tags=["cart"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(health.router, prefix="/health", tags=["health"])


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: AsyncSession = Depends(get_db_session)):
    products_json = []
    all_categories = [{"name": "All", "slug": "all", "id": 0}]
    cart_data = {"items": [], "total_amount": 0, "items_count": 0}

    try:
        from app.coffeeshop.services.product_service import ProductService

        product_service = ProductService(db)
        products = await product_service.get_active_products()

        for product in products:
            try:
                product_dict = {
                    "id": product.id,
                    "name": product.name or "",
                    "description": product.description or "",
                    "image_path": product.image_path,
                    "category": {
                        "id": product.category.id if product.category else 0,
                        "name": product.category.name if product.category else "Unknown",
                        "slug": product.category.slug if product.category else "unknown"
                    },
                    "product_sizes": []
                }

                if hasattr(product, 'product_sizes') and product.product_sizes:
                    for ps in product.product_sizes:
                        if ps and ps.size:
                            product_dict["product_sizes"].append({
                                "id": ps.id,
                                "price": float(ps.price),
                                "size": {
                                    "id": ps.size.id,
                                    "name": ps.size.name,
                                    "volume": ps.size.volume,
                                    "unit": ps.size.unit
                                }
                            })

                products_json.append(product_dict)

            except Exception:
                continue

    except Exception:
        pass

    try:
        from app.coffeeshop.services.category_service import CategoryService

        category_service = CategoryService(db)
        categories = await category_service.get_active_categories()

        all_categories = [{"name": "All", "slug": "all", "id": 0}] + [
            {"name": cat.name, "slug": cat.slug, "id": cat.id} for cat in categories
        ]

    except Exception:
        pass

    try:
        from app.coffeeshop.services.session_cart_service import SessionCartService

        async with async_session_factory() as cart_db:
            try:
                cart_service = SessionCartService(cart_db)
                cart = await cart_service.get_cart(request)

                if cart and hasattr(cart, 'items_count'):
                    if cart.items_count > 0:
                        cart_items_list = []

                        try:
                            items = cart.items if hasattr(cart, 'items') else []

                            if items:
                                for item in items:
                                    try:
                                        cart_items_list.append({
                                            "product_name": getattr(item, 'product_name', 'Unknown'),
                                            "size_name": getattr(item, 'size_name', 'Unknown'),
                                            "quantity": getattr(item, 'quantity', 0),
                                            "price": float(getattr(item, 'price', 0)),
                                            "total_price": float(getattr(item, 'total_price', 0)),
                                            "product_size_id": getattr(item, 'product_size_id', 0),
                                            "image_path": getattr(item, 'image_path', None)
                                        })
                                    except Exception:
                                        continue

                        except Exception:
                            pass

                        if cart_items_list:
                            cart_data = {
                                "items": cart_items_list,
                                "total_amount": float(cart.total_amount),
                                "items_count": cart.items_count
                            }

            except Exception:
                pass

    except Exception:
        pass

    try:
        products_json_str = json.dumps(products_json, cls=DecimalEncoder, ensure_ascii=False)
        categories_json_str = json.dumps(all_categories, ensure_ascii=False)

        response = templates.TemplateResponse(
            "layout.html",
            {
                "request": request,
                "products": products_json_str,
                "categories": categories_json_str,
                "cart": cart_data
            }
        )

        return response

    except Exception:
        return templates.TemplateResponse(
            "layout.html",
            {
                "request": request,
                "products": "[]",
                "categories": '[{"name": "All", "slug": "all", "id": 0}]',
                "cart": {"items": [], "total_amount": 0, "items_count": 0},
                "error": "Critical error loading page"
            }
        )


@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(
    product_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        from app.coffeeshop.services.product_service import ProductService

        product_service = ProductService(db)
        product = await product_service.get_product_by_id(product_id)

        if not product:
            return templates.TemplateResponse(
                "partials/error.html",
                {"request": request, "error": "Product not found", "status_code": 404}
            )

        return templates.TemplateResponse(
            "product_detail.html",
            {
                "request": request,
                "product": product
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": str(e)}
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
