from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from app.models import app_models
from app.repositories.admin_repository import AdminRepository


class AdminService:
    repository: AdminRepository

    def __init__(self, db: AsyncSession) -> None:
        self.repository = AdminRepository(db)

    async def get_request_list(
        self, target_status: Optional[str] = None
    ) -> List[app_models.Request]:
        return await self.repository.get_request_list(target_status)

    async def get_support_requests(self) -> List[app_models.Request]:
        return await self.repository.get_support_requests()

    async def get_request_info(self, request_id: int) -> app_models.Request | None:
        return await self.repository.get_request_info(request_id)

    async def close_request(self, request_id: int):
        return await self.repository.update_request_status(request_id, "closed")

    async def accept_request(self, request_id: int):
        return await self.repository.update_request_status(request_id, "accepted")

    async def reject_request(self, request_id: int, reason: str):
        return await self.repository.reject_request(request_id, reason)

    async def get_users(self):
        return await self.repository.get_users()

    async def get_requests(self):
        return await self.repository.get_requests()
