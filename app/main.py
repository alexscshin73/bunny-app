import asyncio
from contextlib import asynccontextmanager, suppress
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.rooms import router as rooms_router
from app.api.users import router as users_router
from app.api.ws import router as ws_router
from app.config import get_settings
from app.services.pipeline import describe_runtime, warm_runtime
from app.services.rooms import get_room_store

logger = logging.getLogger(__name__)


async def _room_cleanup_loop() -> None:
    settings = get_settings()
    store = get_room_store(
        backend=settings.room_store_backend,
        db_path=settings.room_store_path,
        db_url=settings.room_store_url,
        max_participants=settings.room_max_participants,
        ttl_minutes=settings.room_ttl_minutes,
    )
    interval_seconds = max(settings.room_cleanup_interval_seconds, 1)
    while True:
        cleaned_rooms = store.cleanup_expired_rooms()
        if cleaned_rooms:
            logger.info("Pruned %s expired room(s)", cleaned_rooms)
        await asyncio.sleep(interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    get_room_store(
        backend=settings.room_store_backend,
        db_path=settings.room_store_path,
        db_url=settings.room_store_url,
        max_participants=settings.room_max_participants,
        ttl_minutes=settings.room_ttl_minutes,
    )
    await warm_runtime(settings)
    cleanup_task = asyncio.create_task(_room_cleanup_loop())
    try:
        yield
    finally:
        cleanup_task.cancel()
        with suppress(asyncio.CancelledError):
            await cleanup_task


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    static_dir = Path(__file__).parent / "static"
    upload_dir = Path(settings.room_store_path).resolve().parent / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    brand_image_path = Path(__file__).resolve().parent.parent / "bunny-ai.png"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")
    app.include_router(users_router)
    app.include_router(rooms_router)
    app.include_router(ws_router)

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @app.get("/sw.js", include_in_schema=False)
    async def service_worker() -> FileResponse:
        return FileResponse(static_dir / "sw.js", media_type="application/javascript")

    @app.get("/bunny-ai.png", include_in_schema=False)
    async def bunny_ai_image() -> FileResponse:
        return FileResponse(brand_image_path)

    @app.get("/healthz")
    async def healthz() -> dict[str, object]:
        return {
            "status": "ok",
            "room_store": {
                "backend": settings.room_store_backend,
                "max_participants": settings.room_max_participants,
                "ttl_minutes": settings.room_ttl_minutes,
                "cleanup_interval_seconds": settings.room_cleanup_interval_seconds,
            },
            **describe_runtime(settings),
        }

    return app


app = create_app()
