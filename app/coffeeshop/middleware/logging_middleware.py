# app/coffeeshop/middleware/logging_middleware.py
import time
import logging
from fastapi import Request, Response
from typing import Callable

logger = logging.getLogger("requests")


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware for request logging"""
    start_time = time.time()

    # Log incoming request
    logger.info(
        f"Incoming request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )

    # Execute request
    try:
        response = await call_next(request)

        # Calculate process time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time:.3f}s"
        )

        # Add process time header
        response.headers["X-Process-Time"] = str(process_time)

        return response

    except Exception as e:
        # Log error
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} "
            f"- Error: {str(e)} "
            f"- Time: {process_time:.3f}s"
        )
        raise
