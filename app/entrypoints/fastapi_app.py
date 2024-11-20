import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute


from app.adaptaters.dependencies import get_storage_system
from app.adaptaters.log import LogConfig
from app.entrypoints import fastapi_router

logger = logging.getLogger("kognize")


def get_application() -> FastAPI:
    LogConfig().initialize_loggers()

    def use_route_path_as_operation_ids(app: FastAPI) -> None:
        """
        Simplify operation IDs so that generated API clients have simpler function names.

        Theses names may be used by API clients to generate function names.
        The operation_id will have the format "method_path", like "get_users_me".

        See https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/
        """
        for route in app.routes:
            if isinstance(route, APIRoute):
                # The operation_id should be unique.
                # It is possible to set multiple methods for the same endpoint method but it's not considered a good practice.
                method = "_".join(route.methods)
                route.operation_id = method.lower() + route.path.replace("/", "_")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        yield
        logger.info("Shutting down")

    api_router = APIRouter()
    api_router.include_router(fastapi_router.router)

    app = FastAPI(
        title="Kognize",
        lifespan=lifespan,
    )

    app.include_router(api_router)
    use_route_path_as_operation_ids(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    storage_system = get_storage_system()
    storage_system.update_db()
    return app


app = get_application()
