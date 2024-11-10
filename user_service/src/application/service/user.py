from typing import Any, List, Optional
from uuid import UUID

from fastapi import Depends
from src.application.service.auth import AuthHandler
from src.domain.user.interface import UserReadRepository, UserWriteRepository
from src.domain.user.models import (
    CreateUser,
    LoginUser,
    UpdateUser,
    UserReturnData,
    UserTokenResult,
)
from src.infrastructure.base.base_model import BaseResultModel
from src.infrastructure.database.gateways.clickhouse_gateway import ClickHouseManager
from src.infrastructure.database.models import User
from src.infrastructure.exceptions.token_exceptions import Unauthorized
from src.infrastructure.exceptions.user_exceptions import UserNotFound, WrongPassword
from src.infrastructure.server.provider import Provider


class UserReadService:
    def __init__(
        self,
        read_repository: UserReadRepository = Depends(Provider.user_read_registry),
        clickhouse_repository: ClickHouseManager = Depends(Provider.clickhouse_manager),
        auth_handler: AuthHandler = Depends(Provider.auth_handler),
    ):
        self.read_repo = read_repository
        self.auth_repo = auth_handler
        self.clickhouse = clickhouse_repository
        self.model_name = str(User.__tablename__)

    async def get(self, data: UUID) -> Optional[UserReturnData]:
        if result := await self.read_repo.get(user_uuid=data):
            return result
        raise UserNotFound

    async def find(self, filters: Any = None) -> Optional[List[UserReturnData]]:
        return await self.read_repo.find(filters=filters)


class UserWriteService:
    def __init__(
        self,
        read_repository: UserReadRepository = Depends(Provider.user_read_registry),
        write_repository: UserWriteRepository = Depends(
            Provider.user_write_registry,
        ),
        auth_handler: AuthHandler = Depends(Provider.auth_handler),
    ):
        self.read_repo = read_repository
        self.write_repo = write_repository
        self.auth_repo = auth_handler

    async def register(self, data: CreateUser) -> Optional[UserReturnData]:
        _salted_pass = self.auth_repo.encode_pass(data.password, data.login)
        processed_data = data.model_dump()
        processed_data["password"] = _salted_pass
        return await self.write_repo.create(**processed_data)

    async def edit_user(
        self, data: UpdateUser, user_uuid: UUID
    ) -> Optional[UserReturnData]:
        processed_data = data.model_dump()
        processed_data["uuid"] = user_uuid
        return await self.write_repo.update(**processed_data)

    async def delete_user(self, user_uuid: UUID) -> Optional[UserReturnData]:
        return await self.write_repo.delete(user_uuid=user_uuid)

    async def login_user(self, data: LoginUser) -> UserTokenResult:
        user = await self.read_repo.get_by_login(login=data.login)
        if not user:
            raise UserNotFound
        if not await self.auth_repo.verify_password(
            password=data.password,
            salt=data.login,
            encoded_pass=user.password,
        ):
            raise WrongPassword
        access_token = self.auth_repo.encode_token(user_id=user.uuid)
        refresh_token = self.auth_repo.encode_refresh_token(user_id=user.uuid)
        await self.auth_repo.save_tokens_to_session(
            access_token=access_token,
            refresh_token=refresh_token,
            user_uuid=str(user.uuid),
        )
        return UserTokenResult(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def logout_user(self, refresh_token: str) -> BaseResultModel:
        user_uuid = self.auth_repo.decode_refresh_token(token=refresh_token)
        tokens = await self.auth_repo.get_tokens_from_session(user_uuid=user_uuid)
        if not tokens:
            raise Unauthorized
        if tokens["refresh_token"] == refresh_token:
            await self.auth_repo.del_tokes_from_session(user_uuid=user_uuid)
            return BaseResultModel(status=True)
        raise Unauthorized

    async def refresh_token(self, refresh_token: str) -> UserTokenResult:
        user_uuid = self.auth_repo.decode_refresh_token(token=refresh_token)
        tokens = await self.auth_repo.get_tokens_from_session(user_uuid=user_uuid)
        if not tokens:
            raise Unauthorized
        if tokens["refresh_token"] == refresh_token:
            new_tokens = self.auth_repo.refresh_token(refresh_token=refresh_token)
            await self.auth_repo.save_tokens_to_session(
                access_token=new_tokens["new_access_token"],
                refresh_token=new_tokens["new_refresh_token"],
                user_uuid=user_uuid,
            )
            return UserTokenResult(
                access_token=new_tokens["new_access_token"],
                refresh_token=new_tokens["new_refresh_token"],
            )
        raise Unauthorized

    async def check_auth(self, refresh_token: str) -> BaseResultModel:
        user_uuid = self.auth_repo.decode_refresh_token(token=refresh_token)
        tokens = await self.auth_repo.get_tokens_from_session(user_uuid=user_uuid)
        if not tokens:
            raise Unauthorized
        if tokens["refresh_token"] == refresh_token:
            return BaseResultModel(status=True)
        raise Unauthorized
