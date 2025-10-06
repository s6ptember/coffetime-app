# app/coffeeshop/api/orders.py
from fastapi import APIRouter, Depends, Request, Response, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.database import get_db_session
from ..services.session_cart_service import SessionCartService
from ..api.dependencies import get_order_service

router = APIRouter()
templates = Jinja2Templates(directory="app/coffeeshop/templates")

from ..api.dependencies import get_session_cart_service, get_order_service


@router.get("/checkout", response_class=HTMLResponse)
async def checkout_page(
    request: Request,
    cart_service: SessionCartService = Depends(get_session_cart_service)
):
    try:
        cart = await cart_service.get_cart(request)

        if cart.items_count == 0:
            return templates.TemplateResponse(
                "partials/error.html",
                {"request": request, "error": "Your cart is empty"}
            )

        return templates.TemplateResponse(
            "checkout.html",
            {
                "request": request,
                "cart": cart
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": str(e)}
        )


@router.post("", response_class=HTMLResponse)
async def create_order(
    request: Request,
    response: Response,
    customer_name: str = Form(...),
    ready_time: str = Form(...),
    cart_service: SessionCartService = Depends(get_session_cart_service),
    order_service = Depends(get_order_service)
):
    try:
        cart = await cart_service.get_cart(request)

        if cart.items_count == 0:
            return templates.TemplateResponse(
                "partials/error.html",
                {"request": request, "error": "Cart is empty"}
            )

        order = await order_service.create_order(
            customer_name=customer_name,
            ready_time=ready_time,
            cart_items=cart.items
        )

        await cart_service.clear_cart(request, response)

        return templates.TemplateResponse(
            "order_success.html",
            {
                "request": request,
                "order": order,
                "message": f"Order #{order.id} placed successfully!"
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": f"Failed to create order: {str(e)}"}
        )
