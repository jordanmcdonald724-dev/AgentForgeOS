from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass

from fastapi import Request


@dataclass
class _Bucket:
    tokens: float
    last: float


class RateLimiter:
    def __init__(self) -> None:
        rpm_raw = os.getenv("AGENTFORGE_RATE_LIMIT_RPM", "300")
        burst_raw = os.getenv("AGENTFORGE_RATE_LIMIT_BURST", "60")
        enabled_raw = os.getenv("AGENTFORGE_RATE_LIMIT_ENABLED", "true")
        try:
            self.rpm = max(1.0, float(rpm_raw))
        except Exception:
            self.rpm = 300.0
        try:
            self.burst = max(1.0, float(burst_raw))
        except Exception:
            self.burst = 60.0
        self.enabled = enabled_raw.strip().lower() not in {"0", "false", "no", "off"}
        self._rate_per_sec = self.rpm / 60.0
        self._buckets: dict[str, _Bucket] = {}
        self._lock = asyncio.Lock()

    def _key(self, request: Request) -> str:
        ip = request.client.host if request.client else "unknown"
        token = request.headers.get("X-AgentForge-Token", "")
        if token:
            return f"token:{token}"
        return f"ip:{ip}"

    async def allow(self, request: Request) -> bool:
        if not self.enabled:
            return True
        path = request.url.path or ""
        if path.startswith("/ws"):
            return True
        if not path.startswith("/api"):
            return True
        now = time.monotonic()
        key = self._key(request)
        async with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                self._buckets[key] = _Bucket(tokens=self.burst - 1.0, last=now)
                return True
            elapsed = max(0.0, now - bucket.last)
            bucket.last = now
            bucket.tokens = min(self.burst, bucket.tokens + elapsed * self._rate_per_sec)
            if bucket.tokens >= 1.0:
                bucket.tokens -= 1.0
                return True
            return False

