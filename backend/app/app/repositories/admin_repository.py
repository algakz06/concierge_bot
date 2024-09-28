from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.functions import array_agg

from app.models import db_models, app_models


class AdminRepository:
    db: AsyncSession

    def __init__(self, db: AsyncSession):
        self.db = db  # type: ignore

    async def get_request_list(
        self, target_status: Optional[str] = None
    ) -> List[app_models.Request]:
        query = (
            select(
                db_models.Request.id,
                db_models.Request.user_id,
                db_models.Request.created_at,
                db_models.Request.status,
                db_models.Request.theme,
                db_models.User.telegram_username,
                db_models.User.telegram_id,
            )
            .join(db_models.User, db_models.User.id == db_models.Request.user_id)
            .where(
                db_models.Request.theme != "support",
            )
        )
        if target_status is not None and target_status != "all":
            query = query.where(db_models.Request.status == target_status)

        result = await self.db.execute(query)
        requests = result.fetchall()

        return [
            app_models.Request(
                id=request.id,
                user_id=request.user_id,
                created_at=request.created_at,
                theme=request.theme,
                status=request.status,
                telegram_username=request.telegram_username,
                telegram_id=request.telegram_id,
            )
            for request in requests
        ]

    async def get_support_requests(self) -> List[app_models.Request]:
        requests = await self.db.execute(
            select(
                db_models.Request.id,
                db_models.Request.user_id,
                db_models.Request.created_at,
                db_models.Request.status,
                db_models.Request.theme,
                db_models.User.telegram_username,
                db_models.User.telegram_id,
            )
            .join(db_models.User, db_models.User.id == db_models.Request.user_id)
            .where(db_models.Request.theme == "support")
        )
        requests = requests.fetchall()

        return [
            app_models.Request(
                id=request.id,
                user_id=request.user_id,
                created_at=request.created_at,
                theme=request.theme,
                status=request.status,
                telegram_username=request.telegram_username,
                telegram_id=request.telegram_id,
            )
            for request in requests
        ]

    async def get_request_info(self, request_id: int) -> app_models.Request | None:
        request = await self.db.execute(
            select(
                db_models.Request,
                db_models.User.telegram_username,
                db_models.User.telegram_id,
            )
            .join(db_models.User, db_models.User.id == db_models.Request.user_id)
            .where(db_models.Request.id == request_id)
        )
        request = request.first()

        if request is None:
            return None

        if request[0].theme == "sell":
            db_item = await self.db.execute(
                select(
                    db_models.Item,
                    array_agg(db_models.Image.telegram_file_id).label("image_ids"),
                )
                .join(db_models.Image, db_models.Image.item_id == db_models.Item.id)
                .where(db_models.Item.request_id == request_id)
                .group_by(db_models.Item.id)
            )
            db_item = db_item.scalars().all()
            return app_models.Request(
                id=request[0].id,
                user_id=request[0].user_id,
                created_at=request[0].created_at,
                theme=request[0].theme,
                status=request[0].status,
                telegram_username=request[1],
                telegram_id=request[2],
                item=app_models.Item(
                    description=db_item[0].description,
                    price=db_item[0].price,
                    category=db_item[0].category,
                    image_ids=db_item[1],
                ),
            )
        else:
            db_conversation = await self.db.execute(
                select(db_models.Message).where(
                    db_models.Message.request_id == request_id
                )
            )
            db_conversation = db_conversation.scalars().all()
            conversation = {
                message.question: message.content for message in db_conversation
            }
            return app_models.Request(
                id=request[0].id,
                user_id=request[0].user_id,
                created_at=request[0].created_at,
                theme=request[0].theme,
                status=request[0].status,
                telegram_username=request[1],
                telegram_id=request[2],
                conversation=conversation,
            )

    async def update_request_status(self, request_id: int, status: str) -> None:
        request = await self.db.execute(
            select(db_models.Request).where(db_models.Request.id == request_id)
        )
        request = request.scalars().first()
        request.status = status
        await self.db.commit()

    async def reject_request(self, request_id: int, details: str) -> None:
        request = await self.db.execute(
            select(db_models.Request).where(db_models.Request.id == request_id)
        )
        request = request.scalars().first()
        request.status = status
        request.details = details
        await self.db.commit()

    async def get_users(self) -> List[app_models.User]:
        users = await self.db.execute(
            select(
                db_models.User,
                db_models.Subscription.started_at,
                db_models.Subscription.end_at,
                db_models.Subscription.token_quantity,
            ).join(
                db_models.Subscription,
                db_models.User.id == db_models.Subscription.user_id,
            )
        )
        users = users.fetchall()
        return [
            app_models.User(
                user_id=user.id,
                telegram_id=user.telegram_id,
                telegram_username=user.telegram_username,
                phone_number=user.phone_number,
                name=user.name,
                localization=user.localization,
                balance=user.balance,
                subscription=app_models.SubscriptionDuration(
                    started_at=started_at, end_at=end_at, token_quantity=token_quantity
                ),
            )
            for user, started_at, end_at, token_quantity in users
        ]

    async def get_requests(self) -> List[app_models.Request]:
        db_requests = await self.db.execute(
            select(
                db_models.Request.id,
                db_models.Request.user_id,
                db_models.Request.created_at,
                db_models.Request.details,
                db_models.Request.status,
                db_models.Request.theme,
                db_models.User.telegram_username,
                db_models.User.telegram_id,
                db_models.Item.category,
                db_models.Item.price,
                db_models.Item.description,
            )
            .join(db_models.User, db_models.User.id == db_models.Request.user_id)
            .join(
                db_models.Item,
                db_models.Item.request_id == db_models.Request.id,
                isouter=True,
            )
        )
        db_requests = db_requests.fetchall()
        requests = []
        for db_request in db_requests:
            db_conversation = await self.db.execute(
                select(db_models.Message).filter(
                    db_models.Message.request_id == db_request.id
                )
            )
            db_conversation = db_conversation.scalars().all()
            conversation = {
                message.question: message.content for message in db_conversation
            }
            requests.append(
                app_models.Request(
                    id=db_request[0],
                    user_id=db_request[1],
                    created_at=db_request[2],
                    details=db_request[3],
                    status=db_request[4],
                    theme=db_request[5],
                    telegram_username=db_request[6],
                    telegram_id=db_request[7],
                    item=app_models.Item(
                        category=db_request[8],
                        price=db_request[9],
                        description=db_request[10],
                    ),
                    conversation=conversation,
                )
            )

        return requests
