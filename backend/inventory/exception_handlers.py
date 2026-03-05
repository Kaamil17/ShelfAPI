from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from backend.inventory.exceptions import InventoryAPIError
from backend.inventory.schemas import ErrorDetail, ErrorResponse


async def inventory_api_error_handler(request, exc: InventoryAPIError):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.error_code,
            details=[ErrorDetail(message=exc.message)],
        ).model_dump(exclude_none=True)
    )

async def validation_error_handler(request, exc: RequestValidationError):
    details = [ErrorDetail(message=e["msg"]) for e in exc.errors()]
    return JSONResponse(status_code=422, content=ErrorResponse(error="VALIDATION_ERROR", details=details).model_dump(exclude_none=True))
