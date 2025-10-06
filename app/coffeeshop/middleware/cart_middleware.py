# app/coffeeshop/middleware/cart_middleware.py
import uuid
from fastapi import Request, Response
from typing import Callable


async def cart_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware for cart session management"""
    cart_id = request.cookies.get("cart_id")

    if not cart_id:
        cart_id = str(uuid.uuid4())

    request.state.cart_id = cart_id

    response = await call_next(request)

    # Set cookie if it doesn't exist
    if not request.cookies.get("cart_id"):
        response.set_cookie(
            key="cart_id",
            value=cart_id,
            max_age=86400 * 30,  # 30 days
            httponly=True,
            samesite="lax"
        )

    return response
