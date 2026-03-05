from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class InventoryItemRequest(BaseModel):
    productid: Annotated[str, Field(min_length=1)]
    quantity: Annotated[int, Field(ge=0)]
    timestamp: datetime

class InventoryItemResponse(BaseModel):
    id: int
    productid: str
    quantity: int
    timestamp: datetime
    model_config = {"from_attributes": True}

class InventoryBulkUpdateRequest(BaseModel):
    items: Annotated[list[InventoryItemRequest], Field(min_length=1)]

class InventoryListResponse(BaseModel):
    count: int
    limit: int
    offset: int
    items: list[InventoryItemResponse]

class ErrorDetail(BaseModel):
    field: str | None = None
    message: str

class ErrorResponse(BaseModel):
    error: str
    details: list[ErrorDetail] | None = None
    request_id: str | None = None
