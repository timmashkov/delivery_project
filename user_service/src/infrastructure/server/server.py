import asyncio
import logging
from contextlib import asynccontextmanager
from typing import NoReturn, Optional

from fastapi import APIRouter, FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.infrastructure.base.singleton import Singleton


class ApiServer(Singleton):
    def __init__(
        self,
        name: str,
        routers: list[APIRouter] = None,
        start_callbacks: list[callable] = None,
        stop_callbacks: list[callable] = None,
        logging_config: Optional[dict] = None,
        engine: Optional[AsyncEngine] = None,
        session_maker: Optional[AsyncSession] = None,
    ) -> NoReturn:
        self.name = name
        self.logging_config = logging_config
        self.app = FastAPI(
            title=name,
            lifespan=self._lifespan,
        )
        self.admin = Admin(app=self.app, engine=engine, session_maker=session_maker)
        self.routers = routers or []
        self._init_routers()
        self.start_callbacks = start_callbacks or []
        self.stop_callbacks = stop_callbacks or []

    def _init_routers(self):
        for router in self.routers:
            self.app.include_router(router)
        logging.info("Инициализация routers прошла успешно")

    def _init_logger(self) -> None:
        logging.config.dictConfig(self.logging_config)
        logging.info("Инициализация logger прошла успешно")


    @asynccontextmanager
    async def _lifespan(self, _app: FastAPI):
        for callback in self.start_callbacks:
            if asyncio.iscoroutinefunction(callback):
                await callback()
            else:
                await asyncio.to_thread(callback)
        logging.info("Инициализация startup callbacks прошла успешно")

        yield

        for callback in self.stop_callbacks:
            if asyncio.iscoroutinefunction(callback):
                await callback()
            else:
                await asyncio.to_thread(callback)
        logging.info("Инициализация shutdown callbacks прошла успешно")
