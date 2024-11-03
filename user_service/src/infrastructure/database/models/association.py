from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_uuid", "role_uuid", name="idx_unique_user_role"),
        {"extend_existing": True},
    )

    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.uuid"), primary_key=True)
    role_uuid: Mapped[UUID] = mapped_column(ForeignKey("roles.uuid"), primary_key=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint(
            "permission_uuid",
            "role_uuid",
            name="idx_unique_role_permission",
        ),
        {"extend_existing": True},
    )

    permission_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("permissions.uuid"),
        primary_key=True,
    )
    role_uuid: Mapped[UUID] = mapped_column(ForeignKey("roles.uuid"), primary_key=True)
