from datetime import datetime

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from backend.inventory.dependencies import get_db_session
from backend.inventory.schemas import (
    InventoryBulkUpdateRequest,
    InventoryListResponse,
)
from backend.inventory.service import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("/update", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_inventory(
        payload: InventoryBulkUpdateRequest,
        db: AsyncSession = Depends(get_db_session),
) -> Response:
    await InventoryService(db).bulk_insert(payload.items)
    return Response(status_code=status.HTTP_201_CREATED)


# the rates for the rate-limiter is merely an example here
@router.get("/query", response_model=InventoryListResponse, status_code=status.HTTP_200_OK,
            dependencies = [Depends(RateLimiter(times=30, seconds=60))])
async def query_inventory(
        productid: str = Query(..., min_length=1),
        starttimestamp: datetime | None = Query(None),
        endtimestamp: datetime | None = Query(None),
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db_session),
) -> InventoryListResponse:
    return await InventoryService(db).query(productid, starttimestamp, endtimestamp, limit, offset)
