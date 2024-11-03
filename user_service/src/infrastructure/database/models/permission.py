from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.role import Role


class Permission(Base):

    name: Mapped[str] = mapped_column(
        String,
        comment="Человекочитаемое название разрешения",
    )
    layer: Mapped[str] = mapped_column(
        String,
        comment="К чему относится разрешение ('frontend'/'backend'/...)",
    )
    jdata: Mapped[dict] = mapped_column(
        JSONB,
        server_default="{}",
        default={},
        comment="Разрешения",
    )

    roles: Mapped["Role"] = relationship(
        secondary="role_permissions",
        back_populates="permissions",
        lazy="joined",
    )
