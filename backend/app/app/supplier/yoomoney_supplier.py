from yookassa import Configuration, Payment

from app.configs.settings import settings
from app.configs.logger import log
from app.metadata import errors


class YooMoneySupllier:
    CLIENT_ID: str
    SECRET_KEY: str

    def __init__(self) -> None:
        self.CLIENT_ID = settings.YOUMONEY_APP_ID
        self.SECRET_KEY = settings.YOUMONEY_SECRET_KEY
        Configuration.configure(account_id=self.CLIENT_ID, secret_key=self.SECRET_KEY)

    def create_invoice(self, amount: float) -> str:
        try:
            r = Payment.create(
                {
                    "amount": {"value": amount, "currency": "RUB"},
                    "confirmation": {
                        "type": "redirect",
                        "return_url": settings.APP_URL,
                    },
                }
            )
        except TypeError as e:
            log.error(f"Error occured while creating payment: {e}")
            raise errors.YouMoneyPaymentCreationError

        return r.id, r.confirmation.confirmation_url  # type: ignore

    def check_invoice(self, invoice_id: str) -> bool:
        try:
            r = Payment.find_one(invoice_id)
        except ValueError as e:
            log.error(
                f"Error occured while finding payment with id: {invoice_id}. Error: {e}"
            )
            raise errors.YouMoneyPaymentFindingError

        if r.status == "succeeded":
            return True
        return False
