from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import time
import uuid
import logging

logger = logging.getLogger(__name__)

class EnterpriseLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        
        logger.info(
            f"API Request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url.path),
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
            }
        )
        return response
