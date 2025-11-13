from fastapi import FastAPI
from app.router.router import router
from app.worker.avto_conection_params import avto_conection_params
import asyncio
import logging

logger = logging.getLogger("fastapi_worker")

def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Background Service")
    app.include_router(router)

    @app.on_event("startup")
    async def on_startup():
        logger.info("Starting background worker...")
        asyncio.create_task(avto_conection_params())
    return app