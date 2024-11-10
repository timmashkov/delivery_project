import logging
from typing import Any, Optional, Union
from uuid import UUID

from clickhouse_driver import Client
from pypika import Query, Table
from src.infrastructure.database.models import Base
from src.infrastructure.server.config import settings
from src.infrastructure.utils.asyncio_utils import run_in_executor


class ClickHouseManager:
    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        logger: logging.Logger = logging,
    ) -> None:
        logging.basicConfig(level=logging.INFO)
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.logger = logger
        self.client = Client(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
        )
        self._options = settings.CLICKHOUSE.TYPES

    @property
    def clickhouse_types(self) -> dict:
        return dict(self._options)

    @staticmethod
    def __build_filter_query(query: Any, filters: Any, table: Table) -> str:
        search_params = filters.__dict__
        for key, value in search_params.items():
            if value and table[key]:
                query = query.where(table[key] == value)
        return str(query)

    async def select_object(self, table: str, uuid: Union[str, UUID]):
        table = Table(table)
        query = Query.from_(table).select("*").where(table.uuid == uuid)
        query = str(query)
        return await run_in_executor(
            func=self.client.execute,
            query=query,
        )

    async def select_objects(self, table: str, filters: Optional[Any] = None):
        table = Table(table)
        query = Query.from_(table).select("*")
        if filters:
            query = self.__build_filter_query(query=query, filters=filters, table=table)
        query = str(query)
        return await run_in_executor(
            func=self.client.execute,
            query=query,
        )

    async def insert_object(self, table: str, data: dict):
        t = Table(table)
        query = Query.into(t).columns(*data.keys()).insert(*data.values())
        query = str(query)
        return await run_in_executor(
            func=self.client.execute,
            query=query,
        )

    async def update_object(self, table: str, update_data: dict, filters: Any):
        table = Table(table)
        query = Query.update(table)

        for key, value in update_data.items():
            query = query.set(table[key], value)
        if filters:
            query = self.__build_filter_query(query=query, filters=filters, table=table)

        query = str(query)
        return await run_in_executor(
            func=self.client.execute,
            query=query,
        )

    async def delete_object(self, table: str, filters: Any):
        table = Table(table)
        query = Query.from_(table).delete()

        if filters:
            query = self.__build_filter_query(query=query, filters=filters, table=table)

        query = str(query)
        return await run_in_executor(
            func=self.client.execute,
            query=query,
        )

    async def __create_table(self, table_name: str, columns: dict, **kwargs) -> None:
        self.logger.info(f"Инициализация создания таблицы {table_name}")
        columns_definition = ", ".join(
            [f"{col_name} {col_type}" for col_name, col_type in columns.items()],
        )
        query = f"""
                CREATE TABLE IF NOT EXISTS
                {self.database}.{table_name}
                ({columns_definition})
                ENGINE = MergeTree ORDER BY uuid
                """
        await run_in_executor(
            func=self.client.execute,
            query=query,
            **kwargs,
        )
        self.logger.info(f"Таблицы {table_name} успешно создана")

    async def create_table(self, model: Base) -> None:
        table_name = model.__tablename__
        columns = {}
        existing_tables = await self.get_tables()
        if table_name not in existing_tables:
            for column in model.__table__.columns:
                column_name = column.name
                column_type = str(column.type)
                columns[column_name] = self.clickhouse_types[column_type]
            await self.__create_table(table_name, columns)
        self.logger.debug(f"{table_name} already exists")

    async def get_tables(self, **kwargs) -> list:
        query = f"SHOW TABLES FROM {self.database}"
        return await run_in_executor(
            func=self.client.execute,
            query=query,
            **kwargs,
        )
