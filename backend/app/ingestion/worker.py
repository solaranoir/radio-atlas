"""Dedicated Render worker; API replicas never own production ingestion."""

import asyncio
import signal

from app.analytics.aggregation.runtime import run_aggregation_runtime
from app.config import get_settings
from app.ingestion.retention import run_retention_runtime
from app.ingestion.runtime import run_ingestion_runtime
from app.logging.logger import configure_logging


async def run_worker() -> None:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for name in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(name, stop.set)
    try:
        async with asyncio.TaskGroup() as tasks:
            workers = [
                tasks.create_task(run_ingestion_runtime()),
                tasks.create_task(run_aggregation_runtime()),
            ]
            retention_days = get_settings().radio_atlas_spot_retention_days
            if retention_days > 0:
                workers.append(tasks.create_task(run_retention_runtime(retention_days)))
            await stop.wait()
            for worker in workers:
                worker.cancel()
    finally:
        for name in (signal.SIGTERM, signal.SIGINT):
            loop.remove_signal_handler(name)


if __name__ == "__main__":
    configure_logging()
    asyncio.run(run_worker())
