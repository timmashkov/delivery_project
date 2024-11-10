from app.application.background import background_process
from app.infrastructure.server.config import settings
from app.infrastructure.server.server import ApiServer

order_service = ApiServer(
    name=settings.NAME,
    routers=[],
    start_callbacks=[background_process.start],
    stop_callbacks=[background_process.close],
).app
