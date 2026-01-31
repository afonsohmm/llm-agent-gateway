from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

class BaseGatewayException(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: dict = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}

class ValidationException(BaseGatewayException):
    def __init__(self, message: str = "Validation failed.", details: dict = None):
        super().__init__(400, "VALIDATION_ERROR", message, details)

class ProviderException(BaseGatewayException):
    def __init__(self, message: str = "Error from the provider.", details: dict = None):
        super().__init__(502, "PROVIDER_ERROR", message, details)

class TimeoutException(BaseGatewayException):
    def __init__(self, message: str = "Request timed out.", details: dict = None):
        super().__init__(504, "TIMEOUT", message, details)
        
class JsonInvalidException(BaseGatewayException):
    def __init__(self, message: str = "Invalid JSON output.", details: dict = None):
        super().__init__(422, "JSON_INVALID", message, details)


async def gateway_exception_handler(request: Request, exc: BaseGatewayException):
    trace_id = getattr(request.state, 'trace_id', 'N/A')
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "trace_id": trace_id,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    trace_id = getattr(request.state, 'trace_id', 'N/A')
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "trace_id": trace_id,
            "error": {
                "code": "HTTP_EXCEPTION",
                "message": exc.detail
            }
        },
    )

def add_exception_handlers(app):
    app.add_exception_handler(BaseGatewayException, gateway_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
