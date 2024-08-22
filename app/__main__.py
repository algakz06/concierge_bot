import asyncio

from aiogram import Bot

from app.configs.Settings import settings
from app.app import build_dispatcher

async def main() -> None:
    bot = Bot(token=settings.TG_TOKEN)
    dp = build_dispatcher()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
