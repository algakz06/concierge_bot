from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

from typing import Callable, Awaitable, Any, Dict

from aiogram.types.callback_query import CallbackQuery
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from app.services.user_service import UserService
from app.metadata.eng import keyboards as eng_keyboards
from app.metadata.ru import keyboards as ru_keyboards


class GetSubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_service = UserService()
        state: FSMContext = data["state"]
        user_data = await state.get_data()
        localization = user_data.get("localization", "")
        if not localization:
            user_id = data["event_from_user"].id
            localization = await user_service.get_user_localization(user_id)

        message = event
        if isinstance(event, CallbackQuery):
            message = event.message
        keyboards = ru_keyboards if localization == "ru" else eng_keyboards
        if not await user_service.is_subscribed(data["event_from_user"].id):
            await message.edit_text(
                text="Услуги доступны только пользователям с подпиской. Оформите подписку"
                if localization == "ru"
                else "Only subscribers can use services. Subscribe first",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Оформить подписку"
                                if localization == "ru"
                                else "Subscribe",
                                callback_data="main_menu:subscription",
                            )
                        ],
                        [keyboards.back_to_menu_button],
                    ]
                ),
            )
            return
        data["localization"] = localization
        return await handler(event, data)
