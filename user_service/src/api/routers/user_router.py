from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from pydantic import BaseModel

from src.application.service.user import UserReadService, UserWriteService
from src.domain.user.models import (
    CreateUser,
    LoginUser,
    UpdateUser,
    UserFilter,
    UserReturnData,
    UserTokenResult,
)
from src.infrastructure.base.base_model import BaseResultModel


class UserRouter:
    api_router = APIRouter(prefix="/user", tags=["User"])
    output_model: BaseModel = UserReturnData
    input_model: BaseModel = CreateUser
    filters: UserFilter = FilterDepends(UserFilter)
    read_service_client: UserReadService = Depends(UserReadService)
    write_service_client: UserWriteService = Depends(UserWriteService)

    @staticmethod
    @api_router.get("/find", response_model=List[output_model])
    async def get_users(
        filters=filters,
        service=read_service_client,
    ) -> List[output_model]:
        return await service.find(filters=filters)

    @staticmethod
    @api_router.get("/{user_uuid}", response_model=output_model)
    async def show_user(
        user_uuid: UUID,
        service=read_service_client,
    ) -> output_model:
        return await service.get(data=user_uuid)

    @staticmethod
    @api_router.patch("/{user_uuid}", response_model=output_model)
    async def update(
        user_uuid: UUID,
        incoming_data: UpdateUser,
        service=write_service_client,
    ) -> output_model:
        return await service.edit_user(data=incoming_data, user_uuid=user_uuid)

    @staticmethod
    @api_router.delete("/{user_uuid}", response_model=output_model)
    async def delete(
        user_uuid: UUID,
        service=write_service_client,
    ) -> output_model:
        return await service.delete_user(user_uuid=user_uuid)

    @staticmethod
    @api_router.post("/register", response_model=output_model)
    async def register(
        incoming_data: CreateUser,
        service=write_service_client,
    ) -> output_model:
        return await service.register(data=incoming_data)

    @staticmethod
    @api_router.post("/login", response_model=UserTokenResult)
    async def login_user(
        cmd: LoginUser,
        service=write_service_client,
    ) -> UserTokenResult:
        return await service.login_user(data=cmd)

    @staticmethod
    @api_router.post("/logout", response_model=BaseResultModel)
    async def logout_user(
        refresh_token: str,
        service=write_service_client,
    ) -> BaseResultModel:
        return await service.logout_user(refresh_token=refresh_token)

    @staticmethod
    @api_router.get("/refresh", response_model=UserTokenResult)
    async def refresh_user_token(
        refresh_token: str,
        service=write_service_client,
    ) -> UserTokenResult:
        return await service.refresh_token(refresh_token=refresh_token)

    @staticmethod
    @api_router.get("/is_auth", response_model=BaseResultModel)
    async def is_auth(
        refresh_token: str,
        service=write_service_client,
    ) -> BaseResultModel:
        return await service.check_auth(refresh_token=refresh_token)
