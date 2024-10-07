from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🗂️ Виды услуг", callback_data="main_menu:services")],
        [
            InlineKeyboardButton(text="👤 Профиль", callback_data="main_menu:profile"),
            InlineKeyboardButton(
                text="📱 Подписка", callback_data="main_menu:subscription"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📞 Поддержка", callback_data="main_menu:support"
            ),
            InlineKeyboardButton(text="💰 Баланс", callback_data="main_menu:balance"),
        ],
        [
            InlineKeyboardButton(
                text="📂 Мои запросы", callback_data="main_menu:requests"
            )
        ],
        [
            InlineKeyboardButton(
                text="📝 О услугах Консьержа", callback_data="main_menu:about"
            )
        ],
    ]
)

back_to_menu_button = InlineKeyboardButton(
    text="🏠 Назад в меню", callback_data="back:main_menu"
)

balance_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Пополнить", callback_data="balance:top-up")],
        [back_to_menu_button],
    ]
)

back_to_menu = InlineKeyboardMarkup(inline_keyboard=[[back_to_menu_button]])

help_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отправить запрос", callback_data="help:request")],
        [back_to_menu_button],
    ]
)


subscription_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Оформить подписку", callback_data="subscription:buy"
            )
        ],
        [back_to_menu_button],
    ]
)

item_categories_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Техника", callback_data="item_category:technique")],
        [InlineKeyboardButton(text="Одежда", callback_data="item_category:clothes")],
        [
            InlineKeyboardButton(
                text="Украшения", callback_data="item_category:jewellery"
            )
        ],
        [InlineKeyboardButton(text="Другое", callback_data="item_category:other")],
        [back_to_menu_button],
    ]
)

photos_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Сохранить отправленные фотографии и продолжить",
                callback_data="photos:continue",
            )
        ],
        [
            InlineKeyboardButton(
                text="Сбросить отправленные фотографии и отправить новые",
                callback_data="photos:take_new",
            )
        ],
    ]
)

is_item_info_correct_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Все верно. Отправить запрос", callback_data="item_info:correct"
            )
        ],
        [
            InlineKeyboardButton(
                text="Заполнить заявку заново", callback_data="item_info:incorrect"
            )
        ],
    ]
)
