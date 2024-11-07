from typing import Optional
from uuid import UUID

from fastapi import Depends

from src.application.service.auth import AuthHandler
from src.domain.user.interface import UserReadRepository, UserWriteRepository
from src.domain.user.models import CreateUser, UserReturnData
from src.infrastructure.amqp.broker.kafka import KafkaProducer
from src.infrastructure.database.gateways.clickhouse_gateway import ClickHouseManager
from src.infrastructure.database.models import User
from src.infrastructure.server.provider import Provider


class UserReadService:
    def __init__(
        self,
        read_repository: UserReadRepository = Depends(Provider.user_read_registry),
        clickhouse_repository: ClickHouseManager = Depends(
                Provider.clickhouse_manager
        ),
        auth_handler: AuthHandler = Depends(Provider.auth_handler),
        kafka_handler: KafkaProducer = Depends(Provider.producer_client),
    ):
        self.read_repo = read_repository
        self.auth_repo = auth_handler
        self.kafka_repo = kafka_handler
        self.clickhouse = clickhouse_repository
        self.model_name = str(User.__tablename__)

    async def get(self, data: UUID) -> Optional[UserReturnData]:
        if result := await self.read_repo.get(user_uuid=data):
            return result
        raise UserNotFound

    async def get_list(self, parameter: str) -> Optional[List[UserReturnData]]:
        return await self.read_repo.get_list(parameter=parameter)


class UserWriteService:
    def __init__(
        self,
        read_repository: UserReadRepository = Depends(Provider.user_read_registry),
        write_repository: UserWriteRepository = Depends(
            Provider.user_write_registry,
        ),
    ):
        self.read_repo = read_repository
        self.write_repo = write_repository

    async def register(self, data: CreateUser) -> Optional[UserReturnData]:
        _salted_pass = self.auth_repo.encode_pass(data.hashed_password, data.login)
        processed_data = data.model_dump()
        if created_user := await self.write_repo.create(cmd=cmd):
            data_dict = cmd.model_dump()
            data_dict["user_uuid"] = str(created_user.uuid)
            data_dict["event_type"] = "create"
            asyncio.create_task(
                self.kafka_repo.transactional_send_message(
                    message=data_dict,
                    topic=settings.KAFKA.topics.register_topic,
                ),
            )
        return created_user

    async def edit_user(
        self, data: UpdateUser, user_uuid: GetUserByUUID
    ) -> Optional[UserReturnData]:
        if updated_user := await self.write_repo.update(
            cmd=data, user_uuid=user_uuid.uuid
        ):
            data_dict = data.model_dump()
            data_dict["user_uuid"] = str(updated_user.uuid)
            data_dict["event_type"] = "update"
            asyncio.create_task(
                self.kafka_repo.transactional_send_message(
                    message=data_dict,
                    topic=settings.KAFKA.topics.register_topic,
                ),
            )
        return updated_user

    async def delete_user(self, user_uuid: GetUserByUUID) -> Optional[UserReturnData]:
        if deleted_user := await self.write_repo.delete(user_uuid=user_uuid.uuid):
            data_dict = {"user_uuid": str(deleted_user.uuid), "event_type": "delete"}
            asyncio.create_task(
                self.kafka_repo.transactional_send_message(
                    message=data_dict,
                    topic=settings.KAFKA.topics.register_topic,
                ),
            )
        return deleted_user