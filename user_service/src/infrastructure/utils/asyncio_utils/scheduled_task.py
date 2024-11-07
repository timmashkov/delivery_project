import logging
from asyncio import wait_for, sleep, create_task, Task

from tenacity import retry, wait_random


async def repeat(coro_or_future: callable, repeat_timeout: int):
    while True:
        try:
            await wait_for(coro_or_future, timeout=5)
        except TimeoutError:
            logging.error(
                f"Task {coro_or_future.__name__} timed out"
            )
        except Exception as e:
            raise e
        finally:
            await sleep(repeat_timeout)


def scheduled_task(
    coro_or_future: callable,
    repeat_timeout: int,
) -> Task:
    return create_task(retry(wait=wait_random(min=1, max=10))(repeat)(coro_or_future, repeat_timeout))
