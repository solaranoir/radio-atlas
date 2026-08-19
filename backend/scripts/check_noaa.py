import asyncio

from app.logging.logger import configure_logging
from app.providers.noaa import NOAAProvider


async def main() -> None:
    configure_logging()

    provider = NOAAProvider()

    try:
        observations = await provider.fetch()
        print(f"Received {len(observations)} provider observations")

        for observation in observations:
            print(f"Provider: {observation.provider}")

            for key, value in observation.data.items():
                if key == "cells":
                    print(f"{key}: {len(value)} cells")
                else:
                    print(f"{key}: {value}")

    finally:
        await provider.aclose()


asyncio.run(main())
