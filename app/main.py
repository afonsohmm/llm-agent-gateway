from fastapi import FastAPI
from .api import routes as api_routes
from .core.config import settings
from .api.middleware import TimingAndTraceMiddleware
from .core.concurrency import ConcurrencyLimiterMiddleware, RequestSizeLimiterMiddleware
from .core.errors import add_exception_handlers

app = FastAPI(
    title="LLM Agent Gateway",
    version="0.1.0",
)

# Add middleware
app.add_middleware(TimingAndTraceMiddleware)
app.add_middleware(ConcurrencyLimiterMiddleware)
app.add_middleware(RequestSizeLimiterMiddleware)

# Add exception handlers
add_exception_handlers(app)

# Include API routes
app.include_router(api_routes.router)

@app.on_event("startup")
async def startup_event():
    pass

@app.on_event("shutdown")
async def shutdown_event():
    pass
