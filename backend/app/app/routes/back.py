from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.metadata import admin_keyboards
from app.metadata.ru import keyboards as ru_keyboards
from app.metadata.eng import keyboards as eng_keyboards
from app.middlewares.get_localization import GetLocalizationMiddleware
from app.utils.template_builder import render_template

router = Router()
router.message.middleware(GetLocalizationMiddleware())
router.callback_query.middleware(GetLocalizationMiddleware())


@router.callback_query(F.data.startswith("back"))
async def back(callback: CallbackQuery, localization: str):
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    path = callback.data.split(":")[-1]
    match path:
        case "main_menu":
            await callback.message.edit_text(
                text=render_template(
                    "main_menu.j2", data={"localization": localization}
                ),
                reply_markup=keyboards.main_menu,
            )
        case "services":
            ...
        case "admin":
            await callback.message.edit_text(
                text="<b>Главное меню</b>",
                reply_markup=admin_keyboards.admin_panel_keyboard,
            )
