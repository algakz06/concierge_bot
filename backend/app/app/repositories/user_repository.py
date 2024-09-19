from typing import Dict, List, Union
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.functions import array_agg

from app.configs.db import database_session_manager
from app.models import db_models, app_models
from app.metadata import errors
from app.configs.logger import log


class UserRepository:
    db: AsyncSession

    def __init__(self):
        self.db = database_session_manager.get_session()  # type: ignore

    async def get_user_by_tg_id(self, telegram_id: int) -> Union[app_models.User, None]:
        db_user = await self.db.execute(
            select(db_models.User).where(db_models.User.telegram_id == telegram_id)
        )
        db_user = db_user.scalars().first()
        log.info(f"user in db with tg_id: {telegram_id} is {db_user.__str__()}")
        if db_user is None:
            raise errors.UserNotFound
        return app_models.User(
            user_id=db_user.id,
            telegram_id=db_user.telegram_id,
            telegram_username=db_user.telegram_username,
            name=db_user.name,
            phone_number=db_user.phone_number,
            localization=db_user.localization,
            balance=db_user.balance,
        )

    async def create_user(self, user: app_models.User):
        db_user = db_models.User(
            name=user.name,
            telegram_username=user.telegram_username,
            telegram_id=user.telegram_id,
            localization=user.localization,
            phone_number=user.phone_number,
        )
        self.db.add(db_user)
        await self.db.commit()

    async def get_user_localization(self, telegram_id: int) -> str:
        result = await self.db.execute(
            select(db_models.User.localization).where(
                db_models.User.telegram_id == telegram_id
            )
        )
        localization = result.first()
        if localization is None:
            raise Exception
        return localization[0]

    async def set_localization(self, telegram_id: int, localization: str):
        result = await self.db.execute(
            select(db_models.User).where(db_models.User.telegram_id == telegram_id)
        )
        db_user = result.scalars().first()
        if db_user:
            db_user.localization = localization
            await self.db.commit()

    async def get_user_balance(self, telegram_id: int) -> float:
        result = await self.db.execute(
            select(db_models.User.balance).where(
                db_models.User.telegram_id == telegram_id
            )
        )
        balance = result.first()
        if balance is None:
            raise Exception
        return balance[0]

    async def top_up_balance(self, amount: float, telegram_id: int):
        result = await self.db.execute(
            select(db_models.User).where(db_models.User.telegram_id == telegram_id)
        )
        db_user = result.scalars().first()
        if db_user is None:
            raise errors.UserNotFound
        db_user.balance += amount
        await self.db.commit()

    async def create_request(
        self,
        user_id: int,
        request_theme: str,
    ) -> int:
        db_request = db_models.Request(
            user_id=user_id,
            theme=request_theme,
        )
        self.db.add(db_request)
        await self.db.commit()
        return db_request.id

    async def insert_messages(
        self, request_id: int, conversation: List[Dict[str, str]]
    ) -> None:
        for pair in conversation:
            question, answer = next(iter(pair.items()))
            db_message = db_models.Message(
                request_id=request_id,
                question=question,
                content=answer,
            )
            self.db.add(db_message)
        await self.db.commit()

    async def create_item(self, request_id: int, item: app_models.Item) -> int:
        db_item = db_models.Item(
            request_id=request_id,
            category=item.category,
            description=item.description,
            price=item.price,
        )
        self.db.add(db_item)
        await self.db.commit()

        return db_item.id

    async def insert_images(self, item_id: int, image_ids: List[str]) -> None:
        for image_id in image_ids:
            db_image = db_models.Image(item_id=item_id, telegram_file_id=image_id)
            self.db.add(db_image)
        await self.db.commit()

    async def write_off_balance(
        self, session: AsyncSession, user_id: int, amount: float
    ):
        result = await session.execute(
            select(db_models.User).where(db_models.User.id == user_id)
        )
        db_user = result.scalars().first()
        if db_user is None:
            raise errors.UserNotFound
        if db_user.balance < amount:
            raise errors.NotEnoughMoney
        db_user.balance -= amount

    async def get_user_subscription(
        self, user_id: int
    ) -> app_models.SubscriptionDuration | None:
        result = await self.db.execute(
            select(db_models.Subscription).where(
                db_models.Subscription.user_id == user_id,
                db_models.Subscription.end_at > datetime.datetime.now(),
            )
        )
        subscription = result.scalars().first()
        if subscription is None:
            return subscription
        return app_models.SubscriptionDuration(
            started_at=subscription.started_at, end_at=subscription.end_at
        )

    async def subscribe_user(self, session: AsyncSession, user_id: int, days: int):
        subscription = await self.get_user_subscription(user_id)
        if subscription is not None:
            result = await session.execute(
                select(db_models.Subscription).where(
                    db_models.Subscription.user_id == user_id,
                    db_models.Subscription.end_at == subscription.end_at,
                )
            )
            db_subscription = result.scalars().first()
            db_subscription.end_at = subscription.end_at + datetime.timedelta(days=days)  # type: ignore
            return
        db_subscription = db_models.Subscription(
            user_id=user_id,
            end_at=datetime.datetime.now() + datetime.timedelta(days=days),
        )
        session.add(db_subscription)

    async def write_user_subscription(self, user_id: int, days: int, amount: float):
        try:
            await self.write_off_balance(self.db, user_id, amount)
        except errors.NotEnoughMoney as e:
            await self.db.rollback()
            raise e
        await self.subscribe_user(self.db, user_id, days)
        await self.db.commit()

    async def get_user_requests(self, user_id: int) -> List[app_models.Request]:
        result = await self.db.execute(
            select(db_models.Request).where(db_models.Request.user_id == user_id)
        )
        db_requests = result.scalars().all()
        return [
            app_models.Request(
                id=db_request.id,
                user_id=db_request.user_id,
                created_at=db_request.created_at,
                theme=db_request.theme,
                status=db_request.status,
            )
            for db_request in db_requests
        ]

    async def get_request_info(self, request_id: int) -> app_models.Request | None:
        result = await self.db.execute(
            select(
                db_models.Request,
            ).where(db_models.Request.id == request_id)
        )
        request = result.scalars().first()

        if request is None:
            return None

        if request.theme == "sell":
            result = await self.db.execute(
                select(
                    db_models.Item,
                    array_agg(db_models.Image.telegram_file_id).label("image_ids"),
                )
                .join(db_models.Image, db_models.Image.item_id == db_models.Item.id)
                .where(db_models.Item.request_id == request_id)
                .group_by(db_models.Item.id)
            )
            db_item = result.first()
            return app_models.Request(
                id=request.id,
                user_id=request.user_id,
                created_at=request.created_at,
                theme=request.theme,
                status=request.status,
                details=request.details,
                item=app_models.Item(
                    description=db_item[0].description,
                    price=db_item[0].price,
                    category=db_item[0].category,
                    image_ids=db_item[1],
                ),
            )
        else:
            result = await self.db.execute(
                select(db_models.Message).where(
                    db_models.Message.request_id == request_id
                )
            )
            db_conversation = result.scalars().all()
            conversation = {
                message.question: message.content for message in db_conversation
            }
            return app_models.Request(
                id=request.id,
                user_id=request.user_id,
                created_at=request.created_at,
                theme=request.theme,
                status=request.status,
                details=request.details,
                conversation=conversation,
            )
