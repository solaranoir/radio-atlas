import asyncio

from app.providers.psk_reporter import PSKReporterProvider


async def main() -> None:
    provider = PSKReporterProvider()

    count = 0

    async for spot in provider.stream():
        print(
            spot.sender_callsign.value,
            "->",
            spot.receiver_callsign.value,
            spot.frequency.hz if spot.frequency else None,
            spot.band.value if spot.band else None,
            spot.mode.value,
            spot.snr_db,
            spot.observed_at,
        )

        count += 1

        if count >= 5:
            break


if __name__ == "__main__":
    asyncio.run(main())
