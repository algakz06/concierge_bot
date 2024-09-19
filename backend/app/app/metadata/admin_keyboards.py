from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

admin_panel_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💡 Список запросов", callback_data="admin:requests"
            )
        ],
        [InlineKeyboardButton(text="📬 Поддержка", callback_data="admin:support")],
        [
            InlineKeyboardButton(
                text="📑 Выгрузка статистики", callback_data="admin:upload_stats"
            )
        ],
        [
            InlineKeyboardButton(
                text="💣 Перезагрузить данные", callback_data="admin:reload_data"
            )
        ],
    ]
)

back_to_menu_button = InlineKeyboardButton(
    text="🏠 Вернуться в меню", callback_data="back:admin"
)

back_to_requests_button = InlineKeyboardButton(
    text="💡 Вернуться к запросам", callback_data="admin:requests"
)

back_to_support_requests_button = InlineKeyboardButton(
    text="💡 Вернуться к запросам", callback_data="admin:support"
)

request_keyboard = [
    [
        InlineKeyboardButton(text="Принять в работу", callback_data="request:accept"),
        InlineKeyboardButton(text="Закрыть", callback_data="request:close"),
    ],
    [InlineKeyboardButton(text="Отклонить", callback_data="request:reject")],
]
