import json
import time
from typing import Any

from app.core.config import REDIS_URL


class CacheClient:
    def __init__(self):
        self._memory: dict[str, tuple[float, Any]] = {}
        self._redis = None
        if REDIS_URL:
            try:
                import redis

                self._redis = redis.from_url(REDIS_URL, decode_responses=True)
                self._redis.ping()
            except Exception:
                self._redis = None

    def get(self, key: str):
        if self._redis:
            raw = self._redis.get(key)
            return json.loads(raw) if raw else None

        entry = self._memory.get(key)
        if not entry:
            return None
        expires_at, value = entry
        if expires_at <= time.time():
            self._memory.pop(key, None)
            return None
        return value

    def set(self, key: str, value, ttl_seconds: int = 60):
        if self._redis:
            self._redis.setex(key, ttl_seconds, json.dumps(value, default=str))
            return
        self._memory[key] = (time.time() + ttl_seconds, value)

    def delete_prefix(self, prefix: str):
        if self._redis:
            for key in self._redis.scan_iter(f"{prefix}*"):
                self._redis.delete(key)
            return

        for key in list(self._memory):
            if key.startswith(prefix):
                self._memory.pop(key, None)


cache = CacheClient()
