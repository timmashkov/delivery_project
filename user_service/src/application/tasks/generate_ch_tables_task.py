import asyncio
import logging

from src.infrastructure.database.gateways.clickhouse_gateway import ClickHouseManager
from src.infrastructure.database.models import (
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
)
from src.infrastructure.server.provider import Provider
from src.infrastructure.utils.asyncio_utils import safe_gather


async def create_tables(
    tables: list,
    clickhouse_client: ClickHouseManager = Provider.clickhouse_manager(),
) -> None:
    await safe_gather(
        *[clickhouse_client.create_table(model=table) for table in tables],
    )
    logging.info("Таблицы в Clickhouse созданы")


async def create_tables_task() -> asyncio.Task:
    tables = [User, Role, Permission, RolePermission, UserRole]
    logging.info("Инициализация создания таблиц в Clickhouse")
    return asyncio.create_task(create_tables(tables=tables))
