from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import json

from app.models import app_models
from app.supplier.redis_supplier import RedisSupplier


request_statuses = {"opened": "🔔", "closed": "✅", "rejected": "⛔️", "accepted": "🌀"}


def services(localization: str) -> InlineKeyboardMarkup:
    redis = RedisSupplier()
    raw = json.loads(redis.get_data(localization))
    services = raw["services"]

    buttons = []
    for service in services:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=service[0], callback_data=f"services:{service[0]}:{service[1]}"
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text="Продать вещь" if localization == "ru" else "Sell item",
                callback_data="services:sell",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def prices(localization: str) -> InlineKeyboardMarkup:
    redis = RedisSupplier()
    prices = json.loads(redis.get_data("prices"))
    buttons = []

    for plan in prices:
        days, price = plan["days"], plan["price"]
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{days} дней за {price}₽"
                    if localization == "ru"
                    else f"{days} dasy for {price}₽",
                    callback_data=f"price:{days}-{price}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def requests(
    requests: List[app_models.Request],
    offset: int = 0,
    receiver: str = "admin",
    localization: str = "ru",
) -> InlineKeyboardMarkup:
    buttons = []
    requests.sort(key=lambda x: x.created_at, reverse=True)
    local_requests = (
        requests[offset : offset + 6]
        if offset + 6 < len(requests)
        else requests[offset:]
    )
    for request in local_requests:
        if receiver == "admin":
            text = f"{request_statuses[request.status]} {request.theme} от {request.telegram_username}, {request.created_at.strftime('%d.%m.%Y %H:%M')}"
        else:
            text = (
                f"{request_statuses[request.status]}Запрос №{request.id} от {request.created_at.strftime('%d.%m.%Y')}, {request.theme}"
                if localization == "ru"
                else f"{request_statuses[request.status]}Request #{request.id} from {request.created_at.strftime('%d.%m.%Y')}, {request.theme}"
            )

        buttons.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"admin_requests:{request.id}"
                    if receiver == "admin"
                    else f"user_requests:{request.id}",
                )
            ]
        )
    manage_buttons = []
    if offset != 0:
        manage_buttons.append(
            InlineKeyboardButton(
                text="<<<",
                callback_data=f"admin_requests:prev:{offset-6}"
                if receiver == "admin"
                else f"user_requests:prev:{offset-6}",
            )
        )
    if offset + 6 < len(requests):
        manage_buttons.append(
            InlineKeyboardButton(
                text=">>>",
                callback_data=f"admin_requests:next:{offset+6}"
                if receiver == "admin"
                else f"user_requests:next:{offset+6}",
            )
        )

    buttons.append(manage_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)
