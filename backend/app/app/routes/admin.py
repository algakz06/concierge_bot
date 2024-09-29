from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.configs.bot import bot
from app.configs.db import database_session_manager
from app.services.admin_service import AdminService
from app.supplier.google_sheets_supplier import GoogleSheetSupplier
from app.supplier.redis_supplier import RedisSupplier
from app.metadata import admin_keyboards
from app.utils.keyboard_builder import requests
from app.configs.settings import settings
from app.utils.template_builder import render_template

router = Router()


class AdminGroup(StatesGroup):
    reject_reason = State()


@router.message(F.text == "/admin")
async def admin_panel(message: Message, state: FSMContext):
    if settings.ADMIN_TG_ID != str(message.from_user.id):
        return
    await state.clear()
    await message.answer(
        text="Добро пожаловать", reply_markup=admin_keyboards.admin_panel_keyboard
    )


@router.callback_query(F.data == "admin:requests")
async def get_requests(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открытые", callback_data="requests_category:opened"
                ),
                InlineKeyboardButton(
                    text="Закрытые", callback_data="requests_category:closed"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Отклоненные", callback_data="requests_category:rejected"
                ),
                InlineKeyboardButton(
                    text="Принятые", callback_data="requests_category:accepted"
                ),
            ],
            [InlineKeyboardButton(text="Все", callback_data="requests_category:all")],
        ]
    )
    keyboard.inline_keyboard.append([admin_keyboards.back_to_menu_button])
    await callback.message.edit_text(
        text="Выберите категорию запросов", reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("requests_category:"))
async def get_requests_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":")[-1]
    db = await anext(database_session_manager.get_session())
    admin_service = AdminService(db)
    match category:
        case "all":
            request_list = await admin_service.get_request_list()
        case _:
            request_list = await admin_service.get_request_list(category)
    keyboard = requests(request_list)
    keyboard.inline_keyboard.append([admin_keyboards.back_to_requests_button])
    keyboard.inline_keyboard.append([admin_keyboards.back_to_menu_button])
    await callback.message.edit_text(text="Список запросов", reply_markup=keyboard)
    await state.update_data(request_category=category)


@router.callback_query(F.data == "admin:support")
async def get_support_requests(callback: CallbackQuery):
    db = await anext(database_session_manager.get_session())
    admin_service = AdminService(db)
    support_list = await admin_service.get_support_requests()
    keyboard = requests(support_list)
    keyboard.inline_keyboard.append([admin_keyboards.back_to_menu_button])
    await callback.message.edit_text(text="Список запросов", reply_markup=keyboard)


@router.callback_query(F.data == "admin:reload_data")
async def reload_data(callback: CallbackQuery):
    redis = RedisSupplier()
    gs = GoogleSheetSupplier(redis)  # noqa
    await callback.message.edit_text(
        text="Данные перезагружены",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [admin_keyboards.back_to_menu_button],
            ]
        ),
    )


@router.callback_query(F.data == "admin:upload_stats")
async def upload_stats(callback: CallbackQuery):
    db = await anext(database_session_manager.get_session())
    admin_service = AdminService(db)
    gs = GoogleSheetSupplier(RedisSupplier())

    users = await admin_service.get_users()
    gs.upload_users_statistic(users)

    requests = await admin_service.get_requests()
    gs.upload_request_statistic(requests)

    await callback.message.edit_text(
        text="Статистика загружена",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [admin_keyboards.back_to_menu_button],
            ]
        ),
    )


@router.callback_query(F.data.startswith("admin_requests:"))
async def request_info(callback: CallbackQuery, state: FSMContext):
    db = await anext(database_session_manager.get_session())
    admin_service = AdminService(db)
    action = callback.data.split(":")[1]
    user_data = await state.get_data()
    if action in ["prev", "next"]:
        offset = int(callback.data.split(":")[-1])
        keyboard = requests(
            await admin_service.get_request_list(user_data["request_category"]), offset
        )
        keyboard.inline_keyboard.append([admin_keyboards.back_to_menu_button])
        await callback.message.edit_text(text="Список запросов", reply_markup=keyboard)
        return
    request_id = int(action)
    request_info = await admin_service.get_request_info(request_id)
    await state.update_data(request_id=request_id, request_theme=request_info.theme)
    keyboard = admin_keyboards.request_keyboard
    keyboard = keyboard + [
        [
            admin_keyboards.back_to_requests_button
            if request_info.theme != "support"
            else admin_keyboards.back_to_support_requests_button
        ],
        [admin_keyboards.back_to_menu_button],
    ]
    if request_info.theme == "sell":
        keyboard = keyboard + [
            [
                InlineKeyboardButton(
                    text="Получить фотографии", callback_data="request:get_photos"
                )
            ]
        ]
        await state.update_data(image_ids=request_info.item.image_ids)

    await callback.message.edit_text(
        text=render_template("request_info.j2", data={"request": request_info}),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


@router.callback_query(F.data.startswith("request:"))
async def request_action(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(":")[1]
    user_data = await state.get_data()
    db = await anext(database_session_manager.get_session())
    admin_service = AdminService(db)
    match action:
        case "get_photos":
            for image_id in user_data.get("image_ids", []):
                await bot.send_photo(chat_id=callback.from_user.id, photo=image_id)
        case "close":
            await admin_service.close_request(int(user_data.get("request_id", 0)))
            await callback.message.edit_text(
                text="Запрос закрыт",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            admin_keyboards.back_to_requests_button
                            if user_data.get("request_theme") != "support"
                            else admin_keyboards.back_to_support_requests_button
                        ],
                        [admin_keyboards.back_to_menu_button],
                    ]
                ),
            )
            request = await admin_service.get_request_info(
                int(user_data.get("request_id", 0))
            )
            await bot.send_message(
                chat_id=request.telegram_id,
                text=f"Ваш запрос номер {request.id} на тему {request.theme} закрыт",
            )

        case "accept":
            await admin_service.accept_request(int(user_data.get("request_id", 0)))
            request_info = await admin_service.get_request_info(
                user_data.get("request_id", 0)
            )
            await callback.message.edit_text(
                text="Статус задачи успешно изменен\n\n"
                + render_template("request_info.j2", data={"request": request_info}),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            admin_keyboards.back_to_requests_button
                            if user_data.get("request_theme") != "support"
                            else admin_keyboards.back_to_support_requests_button
                        ],
                        [admin_keyboards.back_to_menu_button],
                    ]
                ),
            )
            request = await admin_service.get_request_info(
                int(user_data.get("request_id", 0))
            )
            await bot.send_message(
                chat_id=request.telegram_id,
                text=f"Ваш запрос номер {request.id} на тему {request.theme} принят",
            )
        case "reject":
            await state.set_state(AdminGroup.reject_reason)
            await callback.message.edit_text(
                text="Введите причину отклонения запроса",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            admin_keyboards.back_to_requests_button
                            if user_data.get("request_theme") != "support"
                            else admin_keyboards.back_to_support_requests_button
                        ],
                        [admin_keyboards.back_to_menu_button],
                    ]
                ),
            )


@router.message(StateFilter(AdminGroup.reject_reason))
async def reject_reason(message: Message, state: FSMContext):
    reason = message.text
    user_data = await state.get_data()
    db = await anext(database_session_manager.get_session())
    admin_service = AdminService(db)
    await admin_service.reject_request(int(user_data.get("request_id", 0)), reason)
    request = await admin_service.get_request_info(int(user_data.get("request_id", 0)))
    await bot.send_message(
        chat_id=request.telegram_id,
        text=f"Ваш запрос номер {request.id} на тему {request.theme} отклонен по причине: {reason}",
    )
    await state.clear()
