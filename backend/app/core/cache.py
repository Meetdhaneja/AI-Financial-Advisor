from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis

from app.core.config import get_settings


class CacheClient:
    def __init__(self) -> None:
        self._client: Redis | None = None
        self._memory_cache: dict[str, Any] = {}

    async def connect(self) -> None:
        settings = get_settings()
        try:
            self._client = Redis.from_url(settings.redis_url, decode_responses=True)
            await self._client.ping()
        except Exception:
            self._client = None

    async def disconnect(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self._memory_cache.clear()

    async def get_json(self, key: str) -> Any | None:
        if self._client is None:
            return self._memory_cache.get(key)
        value = await self._client.get(key)
        return json.loads(value) if value else None

    async def set_json(self, key: str, value: Any, expire_seconds: int = 300) -> None:
        if self._client is None:
            self._memory_cache[key] = value
            return
        await self._client.set(key, json.dumps(value), ex=expire_seconds)

    async def delete(self, *keys: str) -> None:
        if not keys:
            return
        if self._client is None:
            for key in keys:
                self._memory_cache.pop(key, None)
            return
        await self._client.delete(*keys)

    async def delete_prefix(self, prefix: str) -> None:
        if self._client is None:
            for key in list(self._memory_cache.keys()):
                if key.startswith(prefix):
                    self._memory_cache.pop(key, None)
            return
        keys = await self._client.keys(f"{prefix}*")
        if keys:
            await self._client.delete(*keys)


cache = CacheClient()
