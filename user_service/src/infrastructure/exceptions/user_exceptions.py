from fastapi import status

from infrastructure.base_entities.base_exception import BaseAPIException


class UserNotFound(BaseAPIException):
    message = "This account does not exists"
    status_code = status.HTTP_404_NOT_FOUND


class UserAlreadyExists(BaseAPIException):
    message = "This account already exists"
    status_code = status.HTTP_403_FORBIDDEN


class WrongPassword(BaseAPIException):
    message = "Wrong password"
    status_code = status.HTTP_401_UNAUTHORIZED
