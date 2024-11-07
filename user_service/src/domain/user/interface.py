from abc import ABC, abstractmethod
from typing import Any, Generic

from src.domain.user import table_type


class UserReadRepository(ABC, Generic[table_type]):
    def __init__(self):
        self.model = table_type

    @abstractmethod
    async def get(self, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, **kwargs) -> Any:
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
