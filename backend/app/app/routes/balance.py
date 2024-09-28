from typing_extensions import Union
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.configs.db import database_session_manager
from app.metadata.eng import keyboards as eng_keyboards
from app.metadata.ru import keyboards as ru_keyboards
from app.services.payment_service import PaymentService
from app.middlewares.get_localization import GetLocalizationMiddleware

router = Router()
router.callback_query.middleware(GetLocalizationMiddleware())
router.message.middleware(GetLocalizationMiddleware())


class BalanceTopUp(StatesGroup):
    choose_amount = State()


@router.callback_query(F.data == "balance:top-up")
async def top_up_balance(callback: CallbackQuery, localization: str, state: FSMContext):
    keyboards = ru_keyboards if localization == "ru" else eng_keyboards
    await state.set_state(BalanceTopUp.choose_amount)
    await callback.message.edit_text(
        text="Выберите сумму, на которую хотите пополнить баланс или введите свою с клавиатуры"
        if localization == "ru"
        else "Choose amount you want top up your balance or type yours one from keyboard",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="14 000₽", callback_data="balance:amount:14000"
                    ),
                    InlineKeyboardButton(
                        text="40 000₽", callback_data="balance:amount:40000"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="250 000₽", callback_data="balance:amount:250000"
                    ),
                    InlineKeyboardButton(
                        text="480 000₽", callback_data="balance:amount:480000"
                    ),
                ],
                [keyboards.back_to_menu_button],
            ]
        ),
    )


@router.callback_query(F.data.startswith("balance:amount"))
@router.message(StateFilter(BalanceTopUp.choose_amount))
async def choose_amount(
    telegram_obj: Union[CallbackQuery, Message], localization: str, state: FSMContext
):
    if isinstance(telegram_obj, CallbackQuery):
        amount = float(telegram_obj.data.split(":")[-1])  # type: ignore
        message = telegram_obj.message
    else:
        amount = float(telegram_obj.text)  # type: ignore
        message = telegram_obj
        await state.set_state(None)
        await message.delete()

    db = await anext(database_session_manager.get_session())
    payment_service = PaymentService(db)
    amount = float(amount)
    invoice = payment_service.get_invoice_url(amount)

    await state.set_data(
        await state.get_data()
        | {"invoice": {"id": invoice.invoice_id, "amount": amount}}
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Пополнить на {amount}₽"
                    if localization == "ru"
                    else f"Top up {amount}₽",
                    url=invoice.payment_url,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Я оплатил" if localization == "ru" else "I paid",
                    callback_data="check_payment",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Отмена" if localization == "ru" else "Cancel",
                    callback_data="cancel",
                )
            ],
        ]
    )
    await message.answer(
        text="Для пополнения нажмите на кнопку ниже"
        if localization == "ru"
        else "For top up click on button below",
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("check_payment"))
async def check_payment(callback: CallbackQuery, localization: str, state: FSMContext):
    user_data = await state.get_data()
    invoice_id, amount = user_data["invoice"]["id"], user_data["invoice"]["amount"]
    db = await anext(database_session_manager.get_session())
    payment_service = PaymentService(db)
    keyboard = ru_keyboards if localization == "ru" else eng_keyboards
    if payment_service.check_invoice(invoice_id):
        await payment_service.top_up_balance(
            amount=amount, telegram_id=callback.from_user.id
        )
        await callback.message.answer(
            f"Баланс пополнен на {amount}₽"
            if localization == "ru"
            else f"Balance topped up by {amount}₽",
            reply_markup=keyboard.back_to_menu,
        )
    else:
        await callback.message.answer(
            "Платеж не найден. Убедитесь, что оплата произошла успешно и попытайтесь снова"
            if localization == "ru"
            else "Payment not found. Make sure your payment was successful and try again."
        )
