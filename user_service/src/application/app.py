from src.infrastructure.server.config import settings
from src.infrastructure.server.server import ApiServer

user_service = ApiServer(
    name=settings.NAME,
    routers=[],
    start_callbacks=[],
).app
