from typing_extensions import Union
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    Message,
)
from aiogram.fsm.context import FSMContext

from app.middlewares.get_localization import GetLocalizationMiddleware
from app.metadata.ru import keyboards as ru_keyboards
from app.metadata.eng import keyboards as eng_keyboards
from app.utils.template_builder import render_template

router = Router()
router.message.middleware(GetLocalizationMiddleware())
router.callback_query.middleware(GetLocalizationMiddleware())


@router.callback_query(F.data == "cancel")
@router.message(F.text == "/cancel")
async def cancel(
    telegram_obj: Union[Message, CallbackQuery], localization: str, state: FSMContext
):
    if isinstance(telegram_obj, CallbackQuery):
        message = telegram_obj.message
    else:
        message = telegram_obj
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    await state.clear()
    await message.answer(
        "<b>🚫 Действие отменено 🚫</b>"
        if localization == "ru"
        else "<b>🚫 Action cancelled 🚫</b>"
    )
    await message.answer(
        render_template("main_menu.j2", data={"localization": localization}),
        reply_markup=keyboards.main_menu,
    )
