from typing import Any


class SerializationError(Exception):
    _message = "Error while serialization"

    def __init__(self, data: Any) -> None:
        self.data = data
        super().__init__(self._message)

    def __str__(self) -> str:
        return f"SerializationError: {self._message} - Data: {self.data}"


class DeserializationError(Exception):
    _message = "Error while deserialization"

    def __init__(self, data: Any) -> None:
        self.data = data
        super().__init__(self._message)

    def __str__(self) -> str:
        return f"DeserializationError: {self._message} - Data: {self.data}"
