from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

from typing import Callable, Awaitable, Any, Dict

from app.services.user_service import UserService


class GetLocalizationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        state: FSMContext = data["state"]
        user_data = await state.get_data()
        localization = user_data.get("localization", "")
        if not localization:
            user_service = UserService()
            user_id = data["event_from_user"].id
            localization = await user_service.get_user_localization(user_id)
        data["localization"] = localization
        return await handler(event, data)
