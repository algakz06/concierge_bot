from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🗂️ Service list", callback_data="main_menu:services"
            )
        ],
        [
            InlineKeyboardButton(text="👤 Profile", callback_data="main_menu:profile"),
            InlineKeyboardButton(
                text="📱 Subscription", callback_data="main_menu:subscription"
            ),
        ],
        [
            InlineKeyboardButton(text="📞 Support", callback_data="main_menu:support"),
            InlineKeyboardButton(text="💰 Balance", callback_data="main_menu:balance"),
        ],
        [
            InlineKeyboardButton(
                text="📂 My requests", callback_data="main_menu:requests"
            )
        ],
        [
            InlineKeyboardButton(
                text="📝 About Concierge services", callback_data="main_menu:about"
            )
        ],
    ]
)


back_to_menu_button = InlineKeyboardButton(
    text="🏠 Back to menu", callback_data="back:main_menu"
)


balance_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Top up", callback_data="balance:top-up")],
        [back_to_menu_button],
    ]
)


back_to_menu = InlineKeyboardMarkup(inline_keyboard=[[back_to_menu_button]])

help_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Send a request", callback_data="help:request")],
        [back_to_menu_button],
    ]
)


subscription_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Subscribe", callback_data="subscription:buy")],
        [back_to_menu_button],
    ]
)

item_categories_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Technique", callback_data="item_category:technique"
            )
        ],
        [InlineKeyboardButton(text="Clothes", callback_data="item_category:clothes")],
        [
            InlineKeyboardButton(
                text="Jewellery", callback_data="item_category:jewellery"
            )
        ],
        [InlineKeyboardButton(text="Other", callback_data="item_category:other")],
        [back_to_menu_button],
    ]
)

photos_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Save photos and continue", callback_data="photos:continue"
            )
        ],
        [
            InlineKeyboardButton(
                text="Drop photos and send new", callback_data="photos:take_new"
            )
        ],
    ]
)


is_item_info_correct_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Information is correct. Send a request",
                callback_data="item_info:correct",
            )
        ],
        [
            InlineKeyboardButton(
                text="Reapply request", callback_data="item_info:incorrect"
            )
        ],
    ]
)
