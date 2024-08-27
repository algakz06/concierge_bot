from aiogram import F, Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove

from app.models import AppModels
from app.services.UserService import UserService
from app.utils.template_builder import render_template

start_router = Router(name=__name__)


class StartGroup(StatesGroup):
    lang = State()
    name = State()
    phone_number = State()


lang_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 ru", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇺🇸 eng", callback_data="lang_eng")],
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


@start_router.message(StartGroup.lang)
async def choose_language_WA(message: Message, state: FSMContext):
    """
    WA — Wrong Action. Users may type eng or ru by keyboard,
    except of choosing it with inline_keyboard
    """
    await message.answer(f"your state is {await state.get_state()}")
    await message.answer(
        render_template("choose_language_WA.j2"), reply_markup=lang_keyboard
    )


@start_router.message(StateFilter(StartGroup.name))
async def get_user_name(message: Message, state: FSMContext):
    await state.set_data(await state.get_data() | {"name": message.text})
    await message.answer(
        f"Приятно познакомиться, {message.text}\n Поделись теперь номером телефона и можем начинать работу",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="SHARE", request_contact=True)]],
        ),
    )
    await state.set_state(StartGroup.phone_number)


@start_router.message(StateFilter(StartGroup.phone_number))
async def get_phone_number(
    message: Message,
    state: FSMContext,
    userService: UserService = UserService(),
):
    if message.contact is None:
        phone_number = message.text
    else:
        phone_number = message.contact.phone_number

    if message.from_user is None:
        return
    if phone_number is None:
        return

    await message.answer("Спасибо")
    user_data: dict = await state.get_data()
    await userService.create_user(
        AppModels.User(
            name=user_data["name"],
            phone_number=phone_number,
            telegram_id=message.from_user.id,
            lang=user_data["lang"]
        )
    )
    await state.clear()


@start_router.message(CommandStart)
async def welcome(
    message: Message,
    state: FSMContext,
    userService: UserService = UserService(),
) -> None:
    if await userService.get_user_by_telegramId(message.from_user.id) is not None:
        message_text: str = render_template("familiar_user.j2")
        await message.answer(message_text, reply_markup=ReplyKeyboardRemove())
        return
    message_text: str = render_template(
        "start.j2", {"username": message.from_user.username}
    )

    await message.answer(message_text, reply_markup=lang_keyboard)
    await state.set_state(StartGroup.lang)


@start_router.callback_query(F.data.startswith("lang"))
async def choose_language(callback: CallbackQuery, state: FSMContext):
    await state.set_data({"lang": callback.data})
    d = {"lang_ru": "русский", "lang_eng": "английский"}
    await callback.message.answer(f"Супер, вы выбрали {d[callback.data]}")
    await state.set_state(StartGroup.name)
    await callback.message.answer(
        "Как к вам обращаться? Введите имя и фамилию через пробел"
    )
