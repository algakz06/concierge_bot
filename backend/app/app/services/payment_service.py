from typing import NamedTuple

from app.supplier.yoomoney_supplier import YooMoneySupllier
from app.repositories.user_repository import UserRepository


class InvoiceDetails(NamedTuple):
    payment_url: str
    invoice_id: str


class PaymentService:
    yoomoney_supplier: YooMoneySupllier
    user_repository: UserRepository

    def __init__(self) -> None:
        self.yoomoney_supplier = YooMoneySupllier()
        self.user_repository = UserRepository()

    def get_invoice_url(self, amount: float) -> InvoiceDetails:
        invoice_id, payment_url = self.yoomoney_supplier.create_invoice(amount)
        return InvoiceDetails(payment_url, invoice_id)

    def check_invoice(self, invoice_id: str) -> bool:
        return self.yoomoney_supplier.check_invoice(invoice_id)

    async def top_up_balance(self, amount: float, telegram_id: int) -> None:
        await self.user_repository.top_up_balance(amount, telegram_id)
