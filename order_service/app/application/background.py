from asyncio import Task, run
from multiprocessing import Process

from app.infrastructure.utils.asyncio_utils import safe_gather, scheduled_task


async def _start_background_tasks():
    tasks: list[Task] = []
    await safe_gather(*tasks)


def start_background_tasks():
    run(_start_background_tasks())


background_process = Process(target=start_background_tasks)
