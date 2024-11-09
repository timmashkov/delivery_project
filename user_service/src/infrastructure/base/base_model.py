from pydantic import BaseModel


class BaseResultModel(BaseModel):
    """
    Base response model
    """

    status: bool
