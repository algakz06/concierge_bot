import json
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from app.configs.settings import settings
from app.configs.bot import bot
from app.configs.db import database_session_manager
from app.middlewares.get_localization import GetLocalizationMiddleware
from app.routes.subscription import SubscriptionFlow
from app.services.user_service import UserService
from app.supplier.redis_supplier import RedisSupplier
from app.utils import keyboard_builder
from app.utils.template_builder import render_template
from app.metadata.ru import keyboards as ru_keyboards
from app.metadata.eng import keyboards as eng_keyboards

router = Router()
router.callback_query.middleware(GetLocalizationMiddleware())
router.message.middleware(GetLocalizationMiddleware())


class HelpRequest(StatesGroup):
    content = State()


@router.message(F.text.in_(["/menu", "menu", "🏡 Главное меню"]))
async def main_menu(message: Message, localization: str):
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    await message.answer(
        render_template("main_menu.j2", data={"localization": localization}),
        reply_markup=keyboards.main_menu,
    )


@router.callback_query(F.data == "main_menu:services")
async def main_menu_services(callback: CallbackQuery, localization: str):
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards

    keyboard = keyboard_builder.services(localization)
    keyboard.inline_keyboard.append([keyboards.back_to_menu_button])
    await callback.message.edit_text(
        text=render_template("services.j2", data={"localization": localization}),
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "main_menu:profile")
async def main_menu_profile(callback: CallbackQuery, localization: str):
    db = await anext(database_session_manager.get_session())
    user_service = UserService(db)
    user = await user_service.get_user_profile(callback.from_user.id)
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    if user is None:
        return
    await callback.message.edit_text(
        render_template(
            "profile.j2",
            data={
                "localization": localization,
                "user": {
                    "id": user.telegram_id,
                    "name": user.name,
                    "phone": user.phone_number,
                    "balance": user.balance,
                    "subscription": user.subscription.end_at.strftime("%d-%m-%Y %H:%M")
                    if user.subscription is not None
                    else "Отсутствует"
                    if localization == "ru"
                    else "No subscription",
                    "token_quantity": user.subscription.token_quantity
                    if user.subscription is not None
                    else 0,
                },
            },
        ),
        reply_markup=keyboards.back_to_menu,
    )


@router.callback_query(F.data == "main_menu:balance")
async def main_menu_balance(callback: CallbackQuery, localization: str):
    db = await anext(database_session_manager.get_session())
    user_service = UserService(db)
    balance = await user_service.get_user_balance(callback.from_user.id)
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    await callback.message.edit_text(
        text=render_template(
            "balance.j2", data={"localization": localization, "balance": balance}
        ),
        reply_markup=keyboards.balance_keyboard,
    )


@router.callback_query(F.data == "main_menu:support")
async def main_menu_support(callback: CallbackQuery, localization: str):
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    await callback.message.edit_text(
        render_template("help.j2", data={"localization": localization}),
        reply_markup=keyboards.help_keyboard,
    )


@router.callback_query(F.data == "help:request")
async def open_help_request(
    callback: CallbackQuery, localization: str, state: FSMContext
):
    text = (
        "Введите ваш запрос одним сообщением"
        if localization == "ru"
        else "Enter your request in one message"
    )
    await callback.message.edit_text(text)
    await state.set_state(HelpRequest.content)


@router.message(StateFilter(HelpRequest.content))
async def help_request(message: Message, state: FSMContext, localization: str):
    db = await anext(database_session_manager.get_session())
    user_service = UserService(db)
    await user_service.register_request(
        telegram_id=message.from_user.id,
        request_theme="support",
        conversation=[{"Введите ваш запрос одним сообщением": message.text}]
        if localization == "ru"
        else [{"Enter your request in one message": message.text}],
    )
    await state.clear()
    await message.answer(
        text="Ваш запрос отправлен"
        if localization == "ru"
        else "Your request has been sent",
        reply_markup=ru_keyboards.main_menu,
    )
    conversation = [{"Введите ваш запрос одним сообщением": message.text}]
    text = "Поступил новый запрос от @{username}\n\n"
    text += "Заказчик, {username}\n"
    text += "Тема, {request_theme}\n"
    text += "Диалог с пользователем:"
    for conv in conversation:
        question, answer = next(iter(conv.items()))
        text += f"\n— {question}\n— {answer}"
    await bot.send_message(
        text=text.format(
            username=message.from_user.username or message.from_user.id,
            request_theme="Поддержка",
        ),
        chat_id=settings.ADMIN_CHAT_ID,
    )


@router.callback_query(F.data == "main_menu:requests")
async def main_menu_requests(callback: CallbackQuery, localization: str):
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    db = await anext(database_session_manager.get_session())
    user_service = UserService(db)
    requests = await user_service.get_user_requests(callback.from_user.id)
    if len(requests) > 0:
        text = (
            "<b>Ваши запросы:</b>" if localization == "ru" else "<b>Your requests:</b>"
        )
    else:
        text = (
            "<b>У вас пока не было запросов</b>"
            if localization == "ru"
            else "<b>You have no requests</b>"
        )
    keyboard = keyboard_builder.requests(
        requests, receiver="user", localization=localization
    )
    keyboard.inline_keyboard.append([keyboards.back_to_menu_button])
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("user_requests:"))
async def request_info(callback: CallbackQuery, localization: str, state: FSMContext):
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    db = await anext(database_session_manager.get_session())
    user_service = UserService(db)
    action = callback.data.split(":")[1]
    if action in ["prev", "next"]:
        offset = int(callback.data.split(":")[-1])
        keyboard = keyboard_builder.requests(
            await user_service.get_user_requests(callback.from_user.id),
            offset=offset,
            receiver="user",
            localization=localization,
        )
        keyboard.inline_keyboard.append([keyboards.back_to_menu_button])
        await callback.message.edit_text(
            text="Услуги нашего Консьерж-сервиса"
            if localization == "ru"
            else "Our Concierge Service",
            reply_markup=keyboard,
        )
        return
    request_id = int(action)
    request = await user_service.get_request_info(request_id)
    keyboard = keyboards.back_to_menu
    await callback.message.edit_text(
        text=render_template(
            "user_request_info.j2",
            data={
                "request": request,
                "localization": localization,
            },
        ),
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "main_menu:subscription")
async def main_menu_subscription(
    callback: CallbackQuery, localization: str, state: FSMContext
):
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards

    user_service = UserService(await anext(database_session_manager.get_session()))
    if await user_service.get_user_subscription(callback.from_user.id) is None:
        await callback.message.edit_text(
            render_template("new_subscription.j2", data={"localization": localization}),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Активировать пробный период"
                            if localization == "ru"
                            else "Activate trial period",
                            callback_data="price:trial",
                        )
                    ],
                    [keyboards.back_to_menu_button],
                ]
            ),
        )
        await state.set_state(SubscriptionFlow.choose_plan)
        return

    await callback.message.edit_text(
        render_template(
            "subscription.j2",
            data={"localization": localization, "offer_link": settings.TERMS_URL},
        ),
        reply_markup=keyboards.subscription_keyboard,
    )


@router.callback_query(F.data == "main_menu:about")
async def main_menu_about(callback: CallbackQuery, localization: str):
    # text = render_template("about.j2", data={"localization": localization})
    redis = RedisSupplier()
    metadata = json.loads(redis.get_data("metadata")).get("metadata")
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗂️ Услуги" if localization == "ru" else "🗂️ Services",
                    callback_data="main_menu:services",
                )
            ],
            [keyboards.back_to_menu_button],
        ]
    )
    await callback.message.edit_text(
        text=metadata["about_button"][localization], reply_markup=keyboard
    )
