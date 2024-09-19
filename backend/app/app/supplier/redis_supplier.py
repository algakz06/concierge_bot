from typing import Any
from redis import Redis

from app.configs.settings import settings


class RedisSupplier:
    def __init__(self) -> None:
        self.r = Redis.from_url(settings.REDIS_URL)

    def store_data(self, key: str, value: Any):
        self.r.set(key, value)

    def get_data(self, key: str) -> Any:
        return self.r.get(key)
