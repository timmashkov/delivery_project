from sqlalchemy import AsyncAdaptedQueuePool, Pool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.infrastructure.base.singleton import Singleton


class AlchemyGateway(Singleton):
    def __init__(
        self,
        host: str,
        port: int,
        dialect: str,
        login: str,
        password: str,
        database: str,
        echo: bool,
        poolclass: Pool = AsyncAdaptedQueuePool,
    ):
        self.dialect = dialect
        self.login = login
        self.password = password
        self.host = host
        self.port = port
        self.echo = echo
        self.database = database

        self._engine = create_async_engine(
            url=self._db_url,
            echo=self.echo,
            poolclass=poolclass,
        )
        self._autocommit_session = self._engine.execution_options(
            isolation_level="AUTOCOMMIT",
        )
        self._transactional_session = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )
        self._async_session_factory = async_sessionmaker(self._autocommit_session)

    @property
    def _db_url(self) -> str:
        return f"postgresql+{self.dialect}://{self.login}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def transactional_session(self):
        return self._transactional_session

    @property
    def async_session_factory(self):
        return self._async_session_factory
