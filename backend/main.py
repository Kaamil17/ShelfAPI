import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi_limiter import FastAPILimiter
from redis.asyncio import from_url
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

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
    app.state.redis = redis
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
    @app.get("/health")
    async def health_check(request: Request):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            db_status = "ok"
        except Exception:
            db_status = "unavailable"

        try:
            await request.app.state.redis.ping()
            redis_status = "ok"
        except Exception:
            redis_status = "unavailable"

        healthy = db_status == "ok" and redis_status == "ok"
        return JSONResponse(
            status_code=200 if healthy else 503,
            content={"db": db_status, "redis": redis_status},
        )

    return app

app = create_app()
