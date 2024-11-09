from abc import ABC, abstractmethod
from typing import Any, Generic, Optional

from src.domain.user import table_type


class UserReadRepository(ABC, Generic[table_type]):
    def __init__(self):
        self.model = table_type

    @abstractmethod
    async def get(self, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_by_login(self, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def find(self, filters: Optional[Any] = None) -> Any:
        raise NotImplementedError


class UserWriteRepository(ABC, Generic[table_type]):
    def __init__(self):
        self.model = table_type

    @abstractmethod
    async def create(self, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def update(self, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, **kwargs) -> Any:
        raise NotImplementedError
