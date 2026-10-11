"""Dedicated Render worker; API replicas never own production ingestion."""

import asyncio
import signal

from app.analytics.aggregation.runtime import run_aggregation_runtime
from app.ingestion.runtime import run_ingestion_runtime
from app.logging.logger import configure_logging


async def run_worker() -> None:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for name in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(name, stop.set)
    try:
        async with asyncio.TaskGroup() as tasks:
            ingestion = tasks.create_task(run_ingestion_runtime())
            aggregation = tasks.create_task(run_aggregation_runtime())
            await stop.wait()
            ingestion.cancel()
            aggregation.cancel()
    finally:
        for name in (signal.SIGTERM, signal.SIGINT):
            loop.remove_signal_handler(name)


if __name__ == "__main__":
    configure_logging()
    asyncio.run(run_worker())
