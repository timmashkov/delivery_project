from asyncio import AbstractEventLoop, get_event_loop
from concurrent.futures import Executor
from functools import partial
from typing import Any, Optional


async def run_in_executor(
    func: callable,
    loop: Optional[AbstractEventLoop] = None,
    executor: Optional[Executor] = None,
    *args,
    **kwargs,
) -> Any:
    loop = loop or get_event_loop()
    return await loop.run_in_executor(executor, partial(func, *args, **kwargs))
