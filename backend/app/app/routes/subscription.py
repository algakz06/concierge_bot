from aiogram import F, Router
from aiogram.filters.state import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from app.configs.db import database_session_manager
from app.metadata.eng import keyboards as eng_keyboards
from app.metadata.ru import keyboards as ru_keyboards
from app.services.user_service import UserService
from app.middlewares.get_localization import GetLocalizationMiddleware
from app.utils import keyboard_builder

router = Router()
router.callback_query.middleware(GetLocalizationMiddleware())


class SubscriptionFlow(StatesGroup):
    choose_plan = State()
    confirm_subscription = State()


@router.callback_query(F.data == "subscription:buy")
async def buy_subscription(
    callback: CallbackQuery, localization: str, state: FSMContext
):
    text = (
        "Выберите тариф для подписки"
        if localization == "ru"
        else "Choose your subscription plan"
    )
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    keyboard = keyboard_builder.prices(localization)
    keyboard.inline_keyboard.append([keyboards.back_to_menu_button])
    await state.set_state(SubscriptionFlow.choose_plan)
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(
    F.data.startswith("price"), StateFilter(SubscriptionFlow.choose_plan)
)
async def choose_plan(callback: CallbackQuery, localization: str, state: FSMContext):
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    if callback.data == "price:trial":
        user_service = UserService(await anext(database_session_manager.get_session()))
        await user_service.subscribe_user(callback.from_user.id, 7, 0, 10)
        await callback.message.edit_text(
            "Вы успешно подписались на пробный период на 7 дней"
            if localization == "ru"
            else "You have successfully subscribed for a 7-day trial period",
            reply_markup=keyboards.back_to_menu,
        )
        return

    days, price, token_quantity = list(
        map(lambda x: int(x), callback.data.split(":")[-1].split("-", maxsplit=2))
    )
    text = (
        f"Вы выбрали план подписки на {days} дней за {price}₽. Верно?"
        if localization == "ru"
        else f"You chosen a {days}-day subscription plan for {price}₽. Right?"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Все верно" if localization == "ru" else "Yes, it's right",
                    callback_data="subscription_plan:yes",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Вернуть к планам"
                    if localization == "ru"
                    else "Get back to plans",
                    callback_data="subscription_plan:no",
                )
            ],
        ]
    )
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(SubscriptionFlow.confirm_subscription)
    await state.set_data(
        await state.get_data()
        | {"price": price, "days": days, "token_quantity": token_quantity}
    )


@router.callback_query(F.data.startswith("subscription_plan"))
async def confirm_subscription(
    callback: CallbackQuery, localization: str, state: FSMContext
):
    answer = callback.data.split(":")[-1]
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    if answer == "yes":
        db = await anext(database_session_manager.get_session())
        user_service = UserService(db)
        user_data = await state.get_data()
        if await user_service.subscribe_user(
            callback.from_user.id,
            user_data["days"],
            user_data["price"],
            user_data["token_quantity"],
        ):
            await callback.message.edit_text(
                text="Подписка оформлена!"
                if localization == "ru"
                else "Successfully subscribed!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[keyboards.back_to_menu_button]]
                ),
            )
            return
        await callback.message.edit_text(
            text="Что-то пошло не так. Проверьте баланс или попытайтесь позже"
            if localization == "ru"
            else "Something went wrong. Check your balance or try again later",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[keyboards.back_to_menu_button]]
            ),
        )
        return

    text = (
        "Выберите тариф для подписки"
        if localization == "ru"
        else "Choose your subscription plan"
    )
    keyboard = keyboard_builder.prices(localization)
    keyboard.inline_keyboard.append([keyboards.back_to_menu_button])
    await state.set_state(SubscriptionFlow.choose_plan)
    await callback.message.edit_text(text=text, reply_markup=keyboard)
