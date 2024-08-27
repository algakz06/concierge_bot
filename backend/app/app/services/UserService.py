from app.metadata import errors
from app.models import AppModels
from app.repositories.UserRepository import UserRepository

class UserService:
    userRepository: UserRepository
    def __init__(self):
        self.userRepository = UserRepository()
    
    async def get_user_by_telegramId(self, telegramId: int):
        try:
            user = self.userRepository.get_user_by_tg_id(telegramId)
        except errors.UserNotFound:
            return None
        return user

    async def create_user(self, user: AppModels.User):
        try:
            self.userRepository.create_user(user)
        except Exception:
            return
