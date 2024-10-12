from aiogram import F, Router
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import json

from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from app.configs.bot import bot
from app.configs.settings import settings
from app.configs.db import database_session_manager
from app.middlewares.get_localization import GetLocalizationMiddleware
from app.middlewares.get_subscription import GetSubscriptionMiddleware
from app.models import app_models
from app.services.user_service import UserService
from app.supplier.redis_supplier import RedisSupplier
from app.metadata.ru import keyboards as ru_keyboards
from app.metadata.eng import keyboards as eng_keyboards
from app.utils.template_builder import render_template

router = Router()
router.message.middleware(GetLocalizationMiddleware())
router.callback_query.middleware(GetSubscriptionMiddleware())


class ServiceFlow(StatesGroup):
    collect_data = State()


class ServiceSellFlow(StatesGroup):
    item_category = State()
    item_info = State()
    photo = State()
    price = State()
    is_request_correct = State()


photo_ids_storage = {}


@router.callback_query(F.data == "services:sell")
async def sell_service(callback: CallbackQuery, localization: str, state: FSMContext):
    text = (
        "Выберите категорию товара" if localization == "ru" else "Choose item category"
    )
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    await state.set_state(ServiceSellFlow.item_category)
    await callback.message.edit_text(
        text=text, reply_markup=keyboards.item_categories_keyboard
    )


@router.callback_query(
    F.data.startswith("item_category"), StateFilter(ServiceSellFlow.item_category)
)
async def collect_item_category(
    callback: CallbackQuery, localization: str, state: FSMContext
):
    user_data = await state.get_data()
    user_data["item"] = {"category": callback.data.split(":")[-1]}
    await state.set_data(user_data)
    text = (
        "Напишите краткое описание товара. Не более двух абзацев"
        if localization == "ru"
        else "Write a short description of item you sell. Not more than two paragraphs"
    )
    await state.set_state(ServiceSellFlow.item_info)
    await callback.message.edit_text(text=text, reply_markup=None)


@router.message(F.text, StateFilter(ServiceSellFlow.item_info))
async def collect_item_description(
    message: Message, localization: str, state: FSMContext
):
    user_data = await state.get_data()
    user_data["item"]["description"] = message.text
    await state.set_data(user_data)

    text = (
        "Отправьте фотографии товара с разных ракурсов. Отправьте 4 фотографии"
        if localization == "ru"
        else "Send photos of item you sell with different angles. Send 4 photos"
    )
    text += (
        "\n\nОтправьте команду /stop, когда закончите отправку фотографий"
        if localization == "ru"
        else "\n\nSend a command /stop when you're done with photos"
    )
    await state.set_state(ServiceSellFlow.photo)
    await message.answer(text=text, reply_markup=None)


@router.message(F.photo, StateFilter(ServiceSellFlow.photo))
async def collect_photo(message: Message, localization: str, state: FSMContext):
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    photo_ids = photo_ids_storage.get(f"{message.from_user.id}", [])
    photo_ids.append(message.photo[0].file_id)
    photo_ids_storage[f"{message.from_user.id}"] = photo_ids

    if len(photo_ids_storage[f"{message.from_user.id}"]) == 4:
        await message.answer(
            text="Вы успешно загрузили 4 фотографии. Больше нельзя. Выберите опцию для продолжения"
            if localization == "ru"
            else "You hot limit for photos. Choose option to continue",
            reply_markup=keyboards.photos_keyboard,
        )
        user_data = await state.get_data()
        user_data["item"]["photos"] = photo_ids_storage.pop(
            f"{message.from_user.id}", []
        )
        await state.set_data(user_data)
        return


@router.callback_query(F.data.startswith("photo"), StateFilter(ServiceSellFlow.photo))
async def got_photo_limit(
    callback: CallbackQuery, localization: str, state: FSMContext
):
    if callback.data.split(":")[-1] == "take_new":
        text = (
            "Отправьте фотографии товара с разных ракурсов. Отправьте 4 фотографии"
            if localization == "ru"
            else "Send photos of item you sell with different angles. Send 4 photos"
        )
        text += (
            "\n\nОтправьте команду /stop, когда закончите отправку фотографий"
            if localization == "ru"
            else "\n\nSend a command /stop when you're done with photos"
        )
        await state.set_state(ServiceSellFlow.photo)
        await callback.message.answer(text=text, reply_markup=None)
        photo_ids_storage.pop(f"{callback.message.from_user.id}", None)
        return
    text = (
        "Укажите желаемую цену или диапозон.\n\nНапример: 5000р, 5000–10.000р"
        if localization == "ru"
        else "Give an approximate price you want. \n\n Like 5000 rubles, 5000–10.000 rubles"
    )
    await state.set_state(ServiceSellFlow.price)
    await callback.message.answer(text=text, reply_markup=None)


@router.message(F.text, StateFilter(ServiceSellFlow.price))
async def collect_item_price(message: Message, localization: str, state: FSMContext):
    user_data = await state.get_data()
    user_data["item"]["price"] = message.text
    await state.set_data(user_data)
    text = render_template(
        "item_info.j2", data={"localization": localization, "item": user_data["item"]}
    )
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    await state.set_state(ServiceSellFlow.is_request_correct)
    await message.answer(
        text=text, reply_markup=keyboards.is_item_info_correct_keyboard
    )


@router.callback_query(
    F.data.startswith("item_info"), StateFilter(ServiceSellFlow.is_request_correct)
)
async def is_request_correct(
    callback: CallbackQuery, localization: str, state: FSMContext
):
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    if callback.data.split(":")[-1] == "incorrect":
        await state.clear()
        text = (
            "Выберите категорию товара"
            if localization == "ru"
            else "Choose item category"
        )
        await state.set_state(ServiceSellFlow.item_category)
        await callback.message.edit_text(
            text=text, reply_markup=keyboards.item_categories_keyboard
        )
        return
    await callback.message.edit_text(
        "Отлично! Ваша заявка зарегистрирована. Наш оператор свяжется с вами в ближайшее время"
        if localization == "ru"
        else "Great! We accepted your request. Our operator will contact you as soon as possible",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[keyboards.back_to_menu_button]]
        ),
    )
    user_data = await state.get_data() or {}
    item = user_data["item"]
    db = await anext(database_session_manager.get_session())
    user_service = UserService(db)
    await user_service.register_sell_request(
        telegram_id=callback.from_user.id,
        item=app_models.Item(
            category=item["category"],
            description=item["description"],
            image_ids=item["photos"],
            price=item["price"],
        ),
    )
    user = await user_service.get_user_by_telegramId(callback.from_user.id)
    text = "Поступил новый запрос от @{username}\n\n"
    text += "Заказчик, {username}\n"
    text += "Тема: Продажа \n"
    text += "Категория товара: {item_category}\n"
    text += "Описание товара: {item_description}\n"
    text += "Желаемая цена: {item_price}"
    await bot.send_message(
        text=text.format(
            username=user.telegram_username or user.telegram_id,
            item_category=item["category"],
            item_description=item["description"],
            item_price=item["price"],
        ),
        chat_id=settings.ADMIN_CHAT_ID,
    )
    await state.clear()


@router.callback_query(F.data.startswith("services"))
async def general_service(
    callback: CallbackQuery, localization: str, state: FSMContext
):
    # id of reply or button. look for google sheet structure to understand
    request_theme, reply_id = callback.data.split(":")[1:]  # type: ignore
    redis = RedisSupplier()
    raw = json.loads(redis.get_data(localization))
    replies = raw["replies"]
    target_id = f"{reply_id}.1"

    user_data = await state.get_data()
    user_data["request_theme"] = request_theme

    await state.set_state(ServiceFlow.collect_data)
    await state.set_data(user_data)

    if (text := replies.get(target_id, None)) is None:
        await callback.message.answer(  # type: ignore
            text="Сформулируйте ваш запрос одним сообщением"
            if localization == "ru"
            else "Send your request with only one message",
        )
        return

    await state.set_data(user_data | {"last_reply_id": target_id})
    await callback.message.answer(text=text)  # type: ignore


@router.message(F.text, StateFilter(ServiceFlow.collect_data))
async def collect(message: Message, localization: str, state: FSMContext):
    # id of reply or button. look for google sheet structure to understand
    user_data = await state.get_data()
    last_reply_id = user_data.get("last_reply_id", None)

    if last_reply_id is None:
        await message.answer(
            "Передаю ваш запрос оператору. Спасибо!"
            if localization == "ru"
            else "Redirected your request to operator. Thank you!"
        )
        db = await anext(database_session_manager.get_session())
        user_service = UserService(db)
        if not user_data.get("conversation", ""):
            user_data["conversation"] = [
                {"Сформулируйте ваш запрос одним сообщением": message.text}
            ]
        await user_service.register_request(
            telegram_id=message.from_user.id,
            request_theme=user_data["request_theme"],
            conversation=user_data["conversation"],
        )
        text = "Поступил новый запрос от @{username}\n\n"
        text += "Заказчик, {username}\n"
        text += "Тема, {request_theme}\n"
        text += "Диалог с пользователем:"
        for conv in user_data["conversation"]:
            question, answer = next(iter(conv.items()))
            text += f"\n— {question}\n— {answer}"
        await bot.send_message(
            text=text.format(
                username=message.from_user.username or message.from_user.id,
                request_theme=user_data["request_theme"],
            ),
            chat_id=settings.ADMIN_CHAT_ID,
        )
        await state.clear()
        return

    redis = RedisSupplier()
    raw = json.loads(redis.get_data(localization))
    replies = raw["replies"]
    target_id = ".".join([last_reply_id[0], str(int(last_reply_id[2]) + 1)])

    conversation = user_data.get("conversation", False) or []
    conversation.append({replies[last_reply_id]: message.text})
    user_data["conversation"] = conversation

    if (text := replies.get(target_id, None)) is None:
        await message.answer(
            "Передаю ваш запрос оператору, он свяжется с вами в ближайшее время! Спасибо!"
            if localization == "ru"
            else "Redirected your request to operator. He will contact you as soon as possible! Thank you!"
        )
        db = await anext(database_session_manager.get_session())
        user_service = UserService(db)
        await user_service.register_request(
            telegram_id=message.from_user.id,
            request_theme=user_data["request_theme"],
            conversation=user_data["conversation"],
        )
        text = "Поступил новый запрос от @{username}\n\n"
        text += "Заказчик, {username}\n"
        text += "Тема, {request_theme}\n"
        text += "Диалог с пользователем:"
        for conv in user_data["conversation"]:
            question, answer = next(iter(conv.items()))
            text += f"\n— {question}\n— {answer}"
        await bot.send_message(
            text=text.format(
                username=message.from_user.username or message.from_user.id,
                request_theme=user_data["request_theme"],
            ),
            chat_id=settings.ADMIN_CHAT_ID,
        )
        await state.clear()
        return

    user_data["last_reply_id"] = target_id
    await state.set_data(user_data)
    await message.answer(text=text)
