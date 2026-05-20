import time
from collections import defaultdict, deque

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS


_requests: dict[str, deque[float]] = defaultdict(deque)


async def rate_limit_middleware(request: Request, call_next):
    forwarded_for = request.headers.get("x-forwarded-for")
    client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else "unknown")
    bucket_key = f"{client_ip}:{request.url.path}"
    now = time.monotonic()
    bucket = _requests[bucket_key]

    while bucket and now - bucket[0] > RATE_LIMIT_WINDOW_SECONDS:
        bucket.popleft()

    if len(bucket) >= RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Please retry shortly."},
        )

    bucket.append(now)
    return await call_next(request)
