from app.infrastructure.server.config import settings
from app.infrastructure.server.server import ApiServer

order_service = ApiServer(
    name=settings.NAME,
    routers=[],
    start_callbacks=[],
).app
