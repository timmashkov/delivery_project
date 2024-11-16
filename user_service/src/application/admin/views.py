from sqladmin import ModelView

from src.infrastructure.database.models import User


class UseAdmin(ModelView, model=User):
    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True
    name = "Users"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "accounts"
    column_list = [
        User.login,
        User.first_name,
        User.last_name,
        User.phone_number,
        User.age,
        User.email
    ]
