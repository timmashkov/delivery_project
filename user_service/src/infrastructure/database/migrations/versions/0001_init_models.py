"""0001_init_models

Revision ID: b09f7f767549
Revises: 
Create Date: 2024-11-03 13:13:01.798078

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b09f7f767549"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "permissions",
        sa.Column(
            "name",
            sa.String(),
            nullable=False,
            comment="Человекочитаемое название разрешения",
        ),
        sa.Column(
            "layer",
            sa.String(),
            nullable=False,
            comment="К чему относится разрешение ('frontend'/'backend'/...)",
        ),
        sa.Column(
            "jdata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
            comment="Разрешения",
        ),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.create_table(
        "roles",
        sa.Column("name", sa.String(), nullable=False, comment="Название"),
        sa.Column(
            "jdata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
            comment="Дополнительные данные",
        ),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "users",
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("login", sa.String(), nullable=False),
        sa.Column("password", sa.Text(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("phone_number", sa.String(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("login"),
        sa.UniqueConstraint("phone_number"),
    )
    op.create_table(
        "role_permissions",
        sa.Column("permission_uuid", sa.UUID(), nullable=False),
        sa.Column("role_uuid", sa.UUID(), nullable=False),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["permission_uuid"],
            ["permissions.uuid"],
        ),
        sa.ForeignKeyConstraint(
            ["role_uuid"],
            ["roles.uuid"],
        ),
        sa.PrimaryKeyConstraint("permission_uuid", "role_uuid", "uuid"),
        sa.UniqueConstraint(
            "permission_uuid", "role_uuid", name="idx_unique_role_permission"
        ),
    )
    op.create_table(
        "user_roles",
        sa.Column("user_uuid", sa.UUID(), nullable=False),
        sa.Column("role_uuid", sa.UUID(), nullable=False),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["role_uuid"],
            ["roles.uuid"],
        ),
        sa.ForeignKeyConstraint(
            ["user_uuid"],
            ["users.uuid"],
        ),
        sa.PrimaryKeyConstraint("user_uuid", "role_uuid", "uuid"),
        sa.UniqueConstraint("user_uuid", "role_uuid", name="idx_unique_user_role"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_roles")
    op.drop_table("role_permissions")
    op.drop_table("users")
    op.drop_table("roles")
    op.drop_table("permissions")
    # ### end Alembic commands ###