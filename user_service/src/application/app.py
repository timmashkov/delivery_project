from src.api.routers.user_router import UserRouter
from src.infrastructure.server.config import settings
from src.infrastructure.server.server import ApiServer

user_service = ApiServer(
    name=settings.NAME,
    routers=[UserRouter.api_router],
    start_callbacks=[],
).app
