from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove

from app.configs.bot import bot
from app.metadata.ru import keyboards as ru_keyboards
from app.metadata.eng import keyboards as eng_keyboards
from app.models import app_models
from app.services.user_service import UserService
from app.utils.template_builder import render_template

start_router = Router(name=__name__)


class StartGroup(StatesGroup):
    localization = State()
    name = State()
    phone_number = State()


localization_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 ru", callback_data="localization:ru")],
        [InlineKeyboardButton(text="🇺🇸 eng", callback_data="localization:eng")],
    ]
)


@start_router.message(
    StateFilter(StartGroup),
    Command("cancel"),
)
@start_router.message(
    StateFilter(StartGroup),
    F.text.casefold() == "cancel",
)
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Окей, увидимся позже. Захочешь вернуться набери /start")


@start_router.message(StartGroup.localization)
async def choose_localization_WA(message: Message, state: FSMContext):
    """
    WA — Wrong Action. Users may type eng or ru by keyboard,
    except of choosing it with inline_keyboard
    """
    await message.answer(
        render_template("registration_choose_localization_WA.j2"),
        reply_markup=localization_keyboard,
    )


@start_router.message(StateFilter(StartGroup.name))
async def get_user_name(message: Message, state: FSMContext):
    user_data = await state.get_data()
    localization = user_data["localization"]
    await state.set_data(user_data | {"name": message.text})
    await message.answer(
        render_template(
            "registration_phone.j2",
            data={"localization": localization, "username": message.text},
        ),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="Поделиться номером телефона"
                        if localization == "ru"
                        else "Share phone number",
                        request_contact=True,
                    )
                ]
            ],
            resize_keyboard=True,
        ),
    )
    await state.set_state(StartGroup.phone_number)


@start_router.message(StateFilter(StartGroup.phone_number))
async def get_phone_number(
    message: Message,
    state: FSMContext,
    user_service: UserService = UserService(),
):
    if message.contact is None:
        phone_number = message.text
    else:
        phone_number = message.contact.phone_number

    if message.from_user is None:
        return
    if phone_number is None:
        return

    user_data: dict = await state.get_data()
    await user_service.create_user(
        app_models.User(
            name=user_data["name"],
            telegram_username=message.from_user.username
            if message.from_user.username is not None
            else "",
            phone_number=phone_number,
            telegram_id=message.from_user.id,
            localization=user_data["localization"],
        )
    )
    keyboards = ru_keyboards if user_data["localization"] == "ru" else eng_keyboards
    await message.answer(
        render_template("welcome.j2", data={"localization": user_data["localization"]}),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🏡 Главное меню")]], resize_keyboard=True
        ),
    )
    await message.answer(
        render_template(
            "new_user.j2", data={"localization": user_data["localization"]}
        ),
        reply_markup=keyboards.main_menu,
    )
    await state.clear()

    counter = 0
    while True:
        try:
            await bot.delete_message(message.chat.id, message.message_id - counter)
            counter += 1
        except Exception:
            break


@start_router.message(F.text == "/start", StateFilter(None))
async def welcome(
    message: Message,
    state: FSMContext,
    user_service: UserService = UserService(),
) -> None:
    if await user_service.get_user_by_telegramId(message.from_user.id) is not None:
        message_text: str = render_template("familiar_user.j2")
        await message.answer(message_text)
        return
    message_text: str = render_template(
        "start.j2", {"username": message.from_user.username}
    )

    await message.answer(message_text, reply_markup=localization_keyboard)
    await state.set_state(StartGroup.localization)


@start_router.callback_query(F.data.startswith("localization"))
async def choose_localization(callback: CallbackQuery, state: FSMContext):
    localization = callback.data.split(":")[-1]
    await state.set_data({"localization": localization})
    d = {"ru": "русский", "eng": "english"}
    await callback.message.answer(
        render_template(
            "registration_localization_chosen.j2",
            data={"localization": localization, "language": d[localization]},
        )
    )
    await state.set_state(StartGroup.name)
    await callback.message.answer(
        render_template("registration_name.j2", data={"localization": localization})
    )
