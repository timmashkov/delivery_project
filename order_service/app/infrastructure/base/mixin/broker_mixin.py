from typing import Any, Union

from orjson import dumps, loads
from src.infrastructure.exceptions.mq_exceptions import (DeserializationError,
                                                         SerializationError)


class BrokerSerializeMixin:

    @classmethod
    def serialize_message(cls, message: Union[str, bytes, list, dict]) -> bytes:
        try:
            if isinstance(message, str):
                return message.encode("utf-8")
            if isinstance(message, (list, dict)):
                return dumps(message)
            return message
        except (ValueError, TypeError):
            raise SerializationError(data=message)

    @classmethod
    def deserialize_message(cls, message: bytes) -> Any:
        try:
            return loads(message)
        except (ValueError, TypeError):
            raise DeserializationError(data=message)
