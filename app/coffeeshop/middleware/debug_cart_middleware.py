# app/coffeeshop/middleware/debug_cart_middleware.py
from fastapi import Request, Response
from typing import Callable


async def debug_cart_middleware(request: Request, call_next: Callable) -> Response:
    response = await call_next(request)
    return response
