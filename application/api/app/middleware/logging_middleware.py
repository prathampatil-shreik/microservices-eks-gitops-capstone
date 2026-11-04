"""
HTTP request/response logging middleware.
Attaches a unique request_id to every request so you can trace
a single request across all log lines.
"""
import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        # Attach request_id so route handlers can reference it
        request.state.request_id = request_id

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"request_id={request_id} "
            f"method={request.method} "
            f"path={request.url.path} "
            f"status={response.status_code} "
            f"duration_ms={duration_ms:.1f}"
        )

        response.headers["X-Request-ID"] = request_id
        return response
