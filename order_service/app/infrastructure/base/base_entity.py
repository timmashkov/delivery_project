from abc import ABC, abstractmethod
from contextlib import contextmanager


class BaseEntity(ABC):
    def __init__(self, class_type, *args, **kwargs) -> None:
        self.class_type = class_type
        self.args = args
        self.kwargs = kwargs

    def override(self, class_object):
        call = self._call

        @contextmanager
        def base_entity_override():
            try:
                self._call = lambda: class_object
                yield self
            finally:
                self._call = call

        return base_entity_override()

    @abstractmethod
    def _call(self):
        pass

    def __call__(self):
        return self._call()
