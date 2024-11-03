from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.permission import Permission
    from src.infrastructure.database.models.user import User


class Role(Base):

    name: Mapped[str] = mapped_column(String, unique=True, comment="Название")

    jdata: Mapped[dict] = mapped_column(
        JSONB,
        server_default="{}",
        default={},
        comment="Дополнительные данные",
    )

    users: Mapped[List["User"]] = relationship(
        secondary="user_roles",
        back_populates="roles",
        lazy="joined",
    )

    permissions: Mapped[List["Permission"]] = relationship(
        secondary="role_permissions",
        back_populates="roles",
        lazy="joined",
    )
