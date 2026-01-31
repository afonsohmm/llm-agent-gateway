import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

class TimingAndTraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        
        start_time = time.time()
        
        # Add trace_id to request state so it can be accessed in endpoints
        request.state.trace_id = trace_id

        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000  # in milliseconds
        
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Process-Time-Ms"] = str(process_time)
        
        return response
