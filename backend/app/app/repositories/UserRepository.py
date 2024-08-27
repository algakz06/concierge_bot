from typing import Union
from sqlalchemy.orm import Session

from app.configs.DB import get_db
from app.models import DBModels, AppModels
from app.metadata import errors
from app.configs.Logger import log


class UserRepository:
    db: Session

    def __init__(self):
        self.db = next(get_db())  # type: ignore

    def get_user_by_tg_id(self, telegram_id: int) -> Union[AppModels.User, None]:
        db_user = (
            self.db.query(DBModels.User)
            .filter(DBModels.User.telegram_id == telegram_id)
            .first()
        )
        log.info(f"user in db with tg_id: {telegram_id} is {db_user.__str__()}")
        if db_user is None:
            raise errors.UserNotFound
        return AppModels.User(
            telegram_id=db_user.telegram_id,
            name=db_user.name,
            phone_number=db_user.phone_number,
            lang=db_user.lang
        )

    def create_user(self, user: AppModels.User):
        db_user = DBModels.User(
            name=user.name,
            telegram_id=user.telegram_id,
            lang=user.lang,
            phone_number=user.phone_number
        )
        self.db.add(db_user)
        self.db.commit()
