import uvicorn
from src.infrastructure.server.config import settings

if __name__ == "__main__":
    uvicorn.run(
        settings.FAST_API_PATH,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOADED,
    )
