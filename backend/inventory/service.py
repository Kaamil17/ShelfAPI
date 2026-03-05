from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.inventory.repository import InventoryRepository
from backend.inventory.schemas import (
    InventoryItemRequest,
    InventoryItemResponse,
    InventoryListResponse,
)


class InventoryService:
    def __init__(self, session: AsyncSession):
        self._repo = InventoryRepository(session)

    async def bulk_insert(self, items: list[InventoryItemRequest]) -> None:
        await self._repo.bulk_insert([item.model_dump() for item in items])

    async def query(
        self,
        productid: str,
        start: datetime | None,
        end: datetime | None,
        limit: int,
        offset: int,
    ) -> InventoryListResponse:
        db_items = await self._repo.query_by_product(productid, start, end, limit, offset)

        return InventoryListResponse(
            count=len(db_items),
            limit=limit,
            offset=offset,
            items=[InventoryItemResponse.model_validate(i) for i in db_items],
        )
