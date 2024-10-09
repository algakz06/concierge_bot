from dataclasses import dataclass
from typing import Annotated, List, Optional, NamedTuple, Dict
import datetime


class Subscription(NamedTuple):
    started_at: datetime.datetime
    end_at: datetime.datetime
    token_quantity: int


class User:
    user_id: Optional[int]
    telegram_username: str
    telegram_id: str
    phone_number: str
    name: str
    localization: Annotated[str, "len <= 3, like ru, eng..."]
    balance: float
    subscription: Optional[Subscription]

    def __init__(
        self,
        name: str,
        phone_number: str,
        telegram_id: str,
        telegram_username: str,
        localization: str,
        user_id: Optional[int] = None,
        balance: float = 0,
        subscription: Optional[Subscription] = None,
    ):
        self.user_id = user_id
        self.name = name
        self.phone_number = phone_number
        self.telegram_username = telegram_username
        self.telegram_id = telegram_id
        self.localization = localization
        self.balance = balance
        self.subscription = subscription


@dataclass
class Item:
    category: str
    description: str
    price: str
    image_ids: Optional[List[str]]

    def __init__(
        self,
        category: str,
        description: str,
        price: str,
        image_ids: Optional[List[str]] = None,
    ) -> None:
        self.category = category
        self.description = description
        self.image_ids = image_ids
        self.price = price


@dataclass
class Request:
    id: int
    user_id: int
    created_at: datetime.datetime
    theme: str
    status: str
    telegram_id: Optional[int]
    item: Optional[Item]
    conversation: Optional[Dict[str, str]]
    telegram_username: Optional[str]
    details: Optional[str]

    def __init__(
        self,
        id: int,
        user_id: int,
        created_at: datetime.datetime,
        theme: str,
        status: str,
        telegram_id: Optional[int] = None,
        conversation: Optional[Dict[str, str]] = None,
        item: Optional[Item] = None,
        telegram_username: Optional[str] = None,
        details: Optional[str] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.telegram_id = telegram_id
        self.created_at = created_at
        self.theme = theme
        self.status = status
        self.conversation = conversation
        self.item = item
        self.telegram_username = telegram_username
        self.details = details
