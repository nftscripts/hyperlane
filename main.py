import random

from typing import Awaitable

from asyncio import (
    create_task,
    gather,
    sleep,
    run
)

from loguru import logger
from config import *

from src.utils.data.mappings import module_handlers
from src.utils.wrappers.decorators import check_gas

from src.utils.data.helper import (
    private_keys,
    active_module,
)


@check_gas
async def process_task(private_key: str, pattern: str) -> None:
    await module_handlers[pattern](private_key)


async def main() -> None:
    tasks = []
    random.shuffle(private_keys)
    for private_key in private_keys:
        patterns = active_module.copy()

        if RANDOMIZE:
            random.shuffle(patterns)

        for pattern in patterns:
            task = create_task(process_task(private_key, pattern))
            tasks.append(task)

            await task
            time_to_sleep = random.randint(MIN_PAUSE, MAX_PAUSE)
            logger.info(f'Sleeping {time_to_sleep} seconds...')
            await sleep(time_to_sleep)

    await gather(*tasks)


def start_event_loop(awaitable: Awaitable[None]) -> None:
    run(awaitable)


if __name__ == '__main__':
    start_event_loop(main())
