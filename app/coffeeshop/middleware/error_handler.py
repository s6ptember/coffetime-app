# app/coffeeshop/middleware/error_handler.py
import logging
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

logger = logging.getLogger("errors")
templates = Jinja2Templates(directory="app/coffeeshop/templates")


async def http_error_handler(request: Request, exc: HTTPException):
    """Handler for HTTP exceptions"""

    # Log error
    logger.error(
        f"HTTP Error {exc.status_code}: {exc.detail} "
        f"- URL: {request.url.path} "
        f"- Method: {request.method} "
        f"- Client: {request.client.host if request.client else 'unknown'}"
    )

    # Special handling for 401 errors on admin routes
    if exc.status_code == 401 and request.url.path.startswith("/admin"):
        # Return JSON response with proper WWW-Authenticate header for Basic Auth
        response = JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.detail,
                "status_code": exc.status_code
            }
        )
        # Copy any authentication headers from the exception
        if hasattr(exc, 'headers') and exc.headers:
            for key, value in exc.headers.items():
                response.headers[key] = value
        return response

    # Return HTML for HTMX requests
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "partials/error.html",
            {
                "request": request,
                "error": exc.detail,
                "status_code": exc.status_code
            },
            status_code=exc.status_code
        )

    # Return JSON for API requests
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


async def general_error_handler(request: Request, exc: Exception):
    """Handler for general exceptions"""

    # Log critical error
    logger.critical(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)} "
        f"- URL: {request.url.path} "
        f"- Method: {request.method} "
        f"- Client: {request.client.host if request.client else 'unknown'}",
        exc_info=True
    )

    # Return appropriate response
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "partials/error.html",
            {
                "request": request,
                "error": "Internal server error occurred",
                "status_code": 500
            },
            status_code=500
        )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "status_code": 500
        }
    )
