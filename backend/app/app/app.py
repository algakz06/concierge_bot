from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from app.configs.Settings import settings
# from app.models.DBModels import init
from app.configs.Logger import log


async def main() -> None:
    # try:
    #     init()
    # except Exception as e:
    #     log.error(f"Error occured while setting up database: {e}")
    #     exit(0)

    try:
        TG_STORAGE = RedisStorage.from_url(settings.REDIS_URL)
    except Exception as e:
        log.error(f"Error occured while connecting to redis: {e}")
        exit(0)

    dp = Dispatcher(storage=TG_STORAGE)
    bot = Bot(token=settings.TG_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

    from app.routes.start_router import start_router

    dp.include_router(start_router)
    await dp.start_polling(bot)
