import time
import secrets
from typing import Dict, Tuple, Optional
from collections import defaultdict
from fastapi import Request, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from config import settings
from .logger import app_logger

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_auth = HTTPBearer(auto_error=False)

def verify_api_key(
    header_key: Optional[str] = Security(api_key_header),
    bearer_creds: Optional[HTTPAuthorizationCredentials] = Security(bearer_auth)
) -> bool:
    """
    Validates API key provided in either 'X-API-Key' header or 'Authorization: Bearer <key>'.
    If settings.require_auth is False, allows all requests.
    Uses constant-time comparison to protect against timing attacks.
    """
    if not settings.require_auth:
        return True

    candidate_key = None
    if header_key:
        candidate_key = header_key.strip()
    elif bearer_creds and bearer_creds.credentials:
        candidate_key = bearer_creds.credentials.strip()

    if not candidate_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide X-API-Key header or Authorization: Bearer token."
        )

    # Constant-time comparison
    is_valid = secrets.compare_digest(candidate_key, settings.api_key)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or unauthorized API key."
        )
    return True

def verify_websocket_auth(query_token: Optional[str], header_key: Optional[str]) -> bool:
    """
    Validates authentication token for incoming WebSocket connections.
    """
    if not settings.require_auth:
        return True

    candidate = query_token or header_key
    if not candidate:
        return False
    return secrets.compare_digest(candidate.strip(), settings.api_key)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    In-memory sliding-window rate limiter per client IP address.
    Configurable via RATE_LIMIT_PER_MINUTE.
    """
    def __init__(self, app, max_requests_per_minute: int = 120):
        super().__init__(app)
        self.max_requests = max_requests_per_minute
        self.window_seconds = 60.0
        # Maps client_ip -> list of timestamps
        self.request_history: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Exclude WebSocket and health checks from rate limiting
        if request.url.path in ("/health", "/api/health", "/ready", "/api/ready") or request.scope.get("type") == "websocket":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean history for this IP
        history = [ts for ts in self.request_history[client_ip] if ts > cutoff]
        if len(history) >= self.max_requests:
            app_logger.warning(f"Rate limit exceeded for client IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Maximum allowed requests is "
                              f"{self.max_requests} per minute."
                }
            )

        history.append(now)
        self.request_history[client_ip] = history

        # Cleanup overall dict periodically if too many keys
        if len(self.request_history) > 10000:
            active_ips = {
                ip: h for ip, h in self.request_history.items()
                if h and h[-1] > cutoff
            }
            self.request_history = defaultdict(list, active_ips)

        return await call_next(request)
