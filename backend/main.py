import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi_limiter import FastAPILimiter
from redis.asyncio import from_url
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.config import settings
from backend.inventory.database import engine
from backend.inventory.exception_handlers import (
    inventory_api_error_handler,
    validation_error_handler,
)
from backend.inventory.exceptions import InventoryAPIError
from backend.inventory.router import router as inventory_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await from_url(settings.redis_url)
    await FastAPILimiter.init(redis)
    yield
    await engine.dispose()


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response


def create_app() -> FastAPI:
    app = FastAPI(title="Inventory Management API", version="1.0.0", lifespan=lifespan)

    # Middlewares
    app.add_middleware(RequestIdMiddleware)

    #Exception handlers
    app.add_exception_handler(InventoryAPIError, inventory_api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)

    # Apps
    app.include_router(inventory_router, prefix="/api")

    # Health check
    @app.get("/")
    async def health_check():
        return {"message": "Healthy"}

    return app

app = create_app()
