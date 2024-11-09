from typing import Any, List, Optional, Union
from uuid import UUID

from asyncpg import UniqueViolationError
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.domain.user.interface import UserReadRepository, UserWriteRepository
from src.infrastructure.database.gateways.alchemy_gateway import AlchemyGateway
from src.infrastructure.database.models import User
from src.infrastructure.exceptions.user_exceptions import UserAlreadyExists


class ReadRepository(UserReadRepository):

    def __init__(self, session_manager: AlchemyGateway) -> None:
        super().__init__()
        self.model = User
        self.transactional_session: async_sessionmaker = (
            session_manager.transactional_session
        )
        self.async_session_factory: async_sessionmaker = (
            session_manager.async_session_factory
        )

    @classmethod
    def __set_filter(cls, query: select, filters: Any = None) -> select:
        if filters:
            query = filters.filter(query)
        return query

    async def find(
        self,
        filters: Any = None,
    ) -> Union[list, select]:
        query = select(self.model)
        query = self.__set_filter(query, filters)
        async with self.async_session_factory() as session:
            result = await session.execute(query)
            return result.scalars().unique().all()

    async def get(self, user_uuid: UUID) -> Optional[User]:
        async with self.async_session_factory() as session:
            stmt = select(self.model).filter(self.model.uuid == user_uuid)
            answer = await session.execute(stmt)
            result = answer.scalars().unique().first()
        return result

    async def get_by_login(self, login: str) -> Optional[User]:
        async with self.async_session_factory() as session:
            stmt = select(self.model).filter(self.model.login == login)
            answer = await session.execute(stmt)
            result = answer.scalars().unique().first()
        return result


class WriteRepository(UserWriteRepository):
    def __init__(self, session_manager: AlchemyGateway):
        super().__init__()
        self.model = User
        self.transactional_session: async_sessionmaker = (
            session_manager.transactional_session
        )
        self.async_session_factory: async_sessionmaker = (
            session_manager.async_session_factory
        )

    async def create(self, **kwargs) -> Optional[User]:
        try:
            async with self.transactional_session() as session:
                stmt = insert(self.model).values(kwargs).returning(self.model)
                result = await session.execute(stmt)
                await session.commit()
                answer = result.scalars().unique().first()
            return answer
        except (UniqueViolationError, IntegrityError):
            raise UserAlreadyExists

    async def update(
        self,
        **kwargs,
    ) -> Optional[User]:
        async with self.transactional_session() as session:
            stmt = (
                update(self.model)
                .values(kwargs)
                .where(self.model.uuid == kwargs["uuid"])
                .returning(self.model)
            )
            result = await session.execute(stmt)
            await session.commit()
            answer = result.scalars().unique().first()
        return answer

    async def delete(self, user_uuid: UUID) -> Optional[User]:
        async with self.transactional_session() as session:
            stmt = (
                delete(self.model)
                .where(self.model.uuid == user_uuid)
                .returning(self.model)
            )
            result = await session.execute(stmt)
            await session.commit()
            answer = result.scalars().unique().first()
        return answer
