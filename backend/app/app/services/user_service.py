from typing import List, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.metadata import errors
from app.models import app_models
from app.repositories.user_repository import UserRepository
from app.configs.logger import log


class UserService:
    repository: UserRepository

    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def get_user_by_telegramId(self, telegram_id: int):
        try:
            user = await self.repository.get_user_by_tg_id(telegram_id)
        except errors.UserNotFound:
            return None
        return user

    async def create_user(self, user: app_models.User):
        try:
            await self.repository.create_user(user)
        except Exception as e:
            log.error(f"Error occured while creating user: {e}")
            return

    async def set_localization(self, user_id: int, localization: str):
        await self.repository.set_localization(user_id, localization)

    async def get_user_localization(self, user_id: int) -> str:
        return await self.repository.get_user_localization(user_id)

    async def get_user_balance(self, user_id: int) -> float:
        return await self.repository.get_user_balance(user_id)

    async def get_user_profile(self, telegram_id: int) -> app_models.User | None:
        user = await self.get_user_by_telegramId(telegram_id)
        if user is None:
            return None
        user.subscription = await self.repository.get_user_subscription(
            user_id=user.user_id
        )
        return user

    async def register_request(
        self,
        telegram_id: int,
        request_theme: str,
        conversation: List[Dict[str, str]],
    ) -> None:
        user = await self.repository.get_user_by_tg_id(telegram_id)
        request_id = await self.repository.create_request(
            user_id=user.user_id,
            request_theme=request_theme,
        )
        await self.repository.insert_messages(
            request_id=request_id, conversation=conversation
        )
        await self.repository.minus_token_quantity(user.user_id)

    async def register_sell_request(
        self, telegram_id: int, item: app_models.Item
    ) -> None:
        user = await self.repository.get_user_by_tg_id(telegram_id)
        request_id = await self.repository.create_request(
            user_id=user.user_id, request_theme="sell"
        )
        item_id = await self.repository.create_item(request_id=request_id, item=item)
        await self.repository.insert_images(item_id, item.image_ids)
        await self.repository.minus_token_quantity(user.user_id)

    async def subscribe_user(
        self, telegram_id: int, days: int, price: float, token_quantity: int
    ) -> bool:
        user = await self.repository.get_user_by_tg_id(telegram_id)
        try:
            await self.repository.write_user_subscription(
                user.user_id, days=days, amount=price, token_quantity=token_quantity
            )
        except errors.NotEnoughMoney:
            return False
        return True

    async def is_subscribed(self, telegram_id: int) -> bool:
        user = await self.repository.get_user_by_tg_id(telegram_id)
        return await self.repository.check_user_subscription(user.user_id)

    async def get_user_requests(self, telegram_id: int) -> List[app_models.Request]:
        user = await self.repository.get_user_by_tg_id(telegram_id)
        return await self.repository.get_user_requests(user.user_id)

    async def get_request_info(self, request_id: int) -> app_models.Request | None:
        return await self.repository.get_request_info(request_id)

    async def get_user_subscription(
        self, telegram_id: int
    ) -> app_models.Subscription | None:
        user = await self.repository.get_user_by_tg_id(telegram_id)
        return await self.repository.get_user_subscription(user.user_id)
