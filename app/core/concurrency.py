import asyncio
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse
from ..core.config import settings

# Concurrency Limiter
semaphore = asyncio.Semaphore(settings.MAX_CONCURRENCY)

class ConcurrencyLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if not await semaphore.acquire():
            return JSONResponse(
                status_code=429,
                content={
                    "ok": False,
                    "trace_id": getattr(request.state, "trace_id", "N/A"),
                    "error": {
                        "code": "RATE_LIMIT",
                        "message": "Too many concurrent requests.",
                    },
                },
            )
        try:
            return await call_next(request)
        finally:
            semaphore.release()

# Request Size Limiter
class RequestSizeLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > settings.MAX_REQUEST_BYTES:
            return JSONResponse(
                status_code=413,
                content={
                    "ok": False,
                    "trace_id": getattr(request.state, "trace_id", "N/A"),
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": f"Request payload exceeds the limit of {settings.MAX_REQUEST_BYTES} bytes.",
                    },
                },
            )
        return await call_next(request)
