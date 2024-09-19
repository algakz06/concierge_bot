from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from app.configs.logger import log
from app.configs.settings import settings


try:
    TG_STORAGE = RedisStorage.from_url(settings.REDIS_URL)
except Exception as e:
    log.error(f"Error occured while connecting to redis: {e}")
    exit(0)

dp = Dispatcher(storage=TG_STORAGE)
bot = Bot(token=settings.TG_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
