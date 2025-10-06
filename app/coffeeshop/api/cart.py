# app/coffeeshop/api/cart.py
from fastapi import APIRouter, Depends, Request, Response, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.database import get_db_session
from ..services.session_cart_service import SessionCartService

router = APIRouter()
templates = Jinja2Templates(directory="app/coffeeshop/templates")

from ..api.dependencies import get_session_cart_service


@router.get("", response_class=HTMLResponse)
async def get_cart(
    request: Request,
    cart_service: SessionCartService = Depends(get_session_cart_service)
):
    try:
        cart = await cart_service.get_cart(request)

        response = templates.TemplateResponse(
            "partials/cart_content.html",
            {
                "request": request,
                "cart": cart
            }
        )

        return response

    except Exception as e:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": str(e)}
        )


@router.post("/add", response_class=HTMLResponse)
async def add_to_cart(
    request: Request,
    product_size_id: int = Form(...),
    quantity: int = Form(1),
    cart_service: SessionCartService = Depends(get_session_cart_service)
):
    try:
        cart_items = cart_service._get_cart_from_request(request)

        product_size = await cart_service._get_product_size(product_size_id)
        if not product_size:
            raise ValueError("Product not found")

        item_key = str(product_size_id)
        if item_key in cart_items:
            cart_items[item_key].quantity += quantity
        else:
            from ..services.session_cart_service import SessionCartItem
            cart_items[item_key] = SessionCartItem(
                product_size_id=product_size_id,
                quantity=quantity
            )

        cart = await cart_service._build_cart_response(cart_items)

        encoded_data = cart_service._encode_cart_data(cart_items)

        html_content = templates.TemplateResponse(
            "partials/cart_content.html",
            {
                "request": request,
                "cart": cart
            }
        ).body.decode('utf-8')

        response = HTMLResponse(content=html_content)

        if encoded_data:
            response.set_cookie(
                key="cart_data",
                value=encoded_data,
                max_age=86400 * 30,
                httponly=False,
                samesite="lax",
                secure=False,
                path="/",
                domain=None
            )

        response.headers["HX-Trigger"] = "cartUpdated"

        return response

    except ValueError as e:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": str(e)}
        )
    except Exception:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": "Failed to add item to cart"}
        )


@router.put("/update/{product_size_id}", response_class=HTMLResponse)
async def update_cart_item(
    product_size_id: int,
    request: Request,
    quantity: int = Form(...),
    cart_service: SessionCartService = Depends(get_session_cart_service)
):
    try:
        cart_items = cart_service._get_cart_from_request(request)

        item_key = str(product_size_id)

        if quantity <= 0:
            if item_key in cart_items:
                del cart_items[item_key]
        else:
            if item_key in cart_items:
                cart_items[item_key].quantity = quantity
            else:
                product_size = await cart_service._get_product_size(product_size_id)
                if product_size:
                    from ..services.session_cart_service import SessionCartItem
                    cart_items[item_key] = SessionCartItem(
                        product_size_id=product_size_id,
                        quantity=quantity
                    )

        cart = await cart_service._build_cart_response(cart_items)

        encoded_data = cart_service._encode_cart_data(cart_items)

        html_content = templates.TemplateResponse(
            "partials/cart_content.html",
            {
                "request": request,
                "cart": cart
            }
        ).body.decode('utf-8')

        response = HTMLResponse(content=html_content)

        response.set_cookie(
            key="cart_data",
            value=encoded_data if encoded_data else "",
            max_age=86400 * 30,
            httponly=False,
            samesite="lax",
            secure=False,
            path="/"
        )

        response.headers["HX-Trigger"] = "cartUpdated"

        return response

    except Exception:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": "Failed to update cart"}
        )


@router.delete("/remove/{product_size_id}", response_class=HTMLResponse)
async def remove_from_cart(
    product_size_id: int,
    request: Request,
    cart_service: SessionCartService = Depends(get_session_cart_service)
):
    try:
        cart_items = cart_service._get_cart_from_request(request)

        item_key = str(product_size_id)
        if item_key in cart_items:
            del cart_items[item_key]

        cart = await cart_service._build_cart_response(cart_items)

        encoded_data = cart_service._encode_cart_data(cart_items)

        html_content = templates.TemplateResponse(
            "partials/cart_content.html",
            {
                "request": request,
                "cart": cart
            }
        ).body.decode('utf-8')

        response = HTMLResponse(content=html_content)

        response.set_cookie(
            key="cart_data",
            value=encoded_data if encoded_data else "",
            max_age=86400 * 30,
            httponly=False,
            samesite="lax",
            secure=False,
            path="/"
        )

        response.headers["HX-Trigger"] = "cartUpdated"

        return response

    except Exception:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": "Failed to remove item"}
        )


@router.delete("/clear", response_class=HTMLResponse)
async def clear_cart(
    request: Request,
    cart_service: SessionCartService = Depends(get_session_cart_service)
):
    try:
        cart = await cart_service._build_cart_response({})

        html_content = templates.TemplateResponse(
            "partials/cart_content.html",
            {
                "request": request,
                "cart": cart
            }
        ).body.decode('utf-8')

        response = HTMLResponse(content=html_content)

        response.set_cookie(
            key="cart_data",
            value="",
            max_age=86400 * 30,
            httponly=False,
            samesite="lax",
            secure=False,
            path="/"
        )

        response.headers["HX-Trigger"] = "cartUpdated"

        return response

    except Exception:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": "Failed to clear cart"}
        )


@router.get("/count", response_class=HTMLResponse)
async def get_cart_count(
    request: Request,
    cart_service: SessionCartService = Depends(get_session_cart_service)
):
    try:
        cart = await cart_service.get_cart(request)

        if cart.items_count > 0:
            return f'{cart.items_count}'
        else:
            return ""
    except Exception:
        return ""
