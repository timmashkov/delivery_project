from asyncio import Task, run
from multiprocessing import Process

from src.application.tasks.generate_ch_tables_task import create_tables_task
from src.infrastructure.server.config import settings
from src.infrastructure.utils.asyncio_utils import safe_gather, scheduled_task


async def _start_background_tasks():
    tasks: list[Task] = [
        scheduled_task(create_tables_task(), settings.REPEAT_TIMEOUT),
    ]
    await safe_gather(*tasks)


def start_background_tasks():
    run(_start_background_tasks())


background_process = Process(target=start_background_tasks)
