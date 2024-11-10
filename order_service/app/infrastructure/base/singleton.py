from user_service.src.infrastructure.base.base_entity import BaseEntity


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs) -> None:
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class OnlyContainer(BaseEntity):
    def __init__(self, class_type, *args, **kwargs):
        self.class_object = None
        super().__init__(class_type, *args, **kwargs)

    def _call(self):
        if not self.class_object:
            self.class_object = self.class_type(*self.args, **self.kwargs)
        return self.class_object
