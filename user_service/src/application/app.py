from src.api.routers.user_router import UserRouter
from src.application.background import background_process
from src.infrastructure.server.config import settings
from src.infrastructure.server.provider import Provider
from src.infrastructure.server.server import ApiServer

user_service = ApiServer(
    name=settings.NAME,
    routers=[UserRouter.api_router],
    start_callbacks=[background_process.start],
    stop_callbacks=[background_process.close],
    engine=Provider.alchemy_manager()._engine,
    session_maker=Provider.alchemy_manager()._async_session_factory,
).app
