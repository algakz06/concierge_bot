from typing import Annotated


class User:
    telegram_id: int
    phone_number: str
    name: str
    lang: Annotated[str, "len <= 3, like ru, eng..."]

    def __init__(self, name: str, phone_number: str, telegram_id: int, lang: str):
        self.name = name
        self.phone_number = phone_number
        self.telegram_id = telegram_id
        self.lang = lang
