import asyncio

from app.providers.psk_reporter import PSKReporterProvider


async def main() -> None:
    provider = PSKReporterProvider()

    count = 0

    async for observation in provider.stream():
        print(f"Provider: {observation.provider}")
        print(f"Observed at: {observation.data['observed_at']}")
        print(f"Sender: {observation.data['sender_callsign']['value']}")
        print(f"Receiver: {observation.data['receiver_callsign']['value']}")
        print(f"Frequency: {observation.data['frequency']['hz']}")
        print(f"Band: {observation.data['band']['value']}")
        print(f"Mode: {observation.data['mode']['value']}")
        print(f"SNR: {observation.data['snr_db']}")
        print()

        count += 1

        if count >= 5:
            break


if __name__ == "__main__":
    asyncio.run(main())
