from aiogram import F, Router
from aiogram.types import Message

from app.middlewares.get_localization import GetLocalizationMiddleware
from app.configs.db import database_session_manager
from app.services.user_service import UserService
from app.utils.template_builder import render_template

router = Router()
router.message.middleware(GetLocalizationMiddleware())


@router.message(F.text == "/change_language")
async def change_localization(message: Message, localization: str):
    localization = {"ru": "eng", "eng": "ru"}[localization]
    language = {"ru": "русский", "eng": "english"}

    db = await anext(database_session_manager.get_session())
    user_service = UserService(db)
    await user_service.set_localization(message.from_user.id, localization)

    await message.answer(
        render_template(
            "localization_changed.j2",
            data={"localization": localization, "language": language[localization]},
        )
    )
