from datetime import datetime

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.inventory.models import InventoryItem


class InventoryRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def bulk_insert(self, items: list[dict]) -> None:
        await self._session.execute(insert(InventoryItem), items)

    async def query_by_product(
        self,
        productid: str,
        start: datetime | None,
        end: datetime | None,
        limit: int,
        offset: int,
    ) -> list[InventoryItem]:
        stmt = (
            select(InventoryItem)
            .where(InventoryItem.productid == productid)
            .order_by(InventoryItem.timestamp.asc())
            .limit(limit)
            .offset(offset)
        )
        if start:
            stmt = stmt.where(InventoryItem.timestamp >= start)
        if end:
            stmt = stmt.where(InventoryItem.timestamp <= end)
        result = await self._session.execute(stmt)

        return list(result.scalars().all())
