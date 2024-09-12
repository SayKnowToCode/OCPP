import asyncio
import logging

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys
    sys.exit(1)

from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus

# Set logging level to show only relevant information
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ChargePoint(cp):
    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
            charge_point_model="Optimus", charge_point_vendor="The Mobility House"
        )

        logging.info("Sending Boot Notification...")

        response = await self.call(request)

        if response.status == RegistrationStatus.accepted:
            logging.info("Connected to central system.")
        else:
            logging.warning(f"Boot Notification was rejected. Status: {response.status}")


async def main():
    try:
        async with websockets.connect(
            "ws://localhost:9000/CP_1", subprotocols=["ocpp1.6"]
        ) as ws:

            cp = ChargePoint("CP_1", ws)

            logging.info(f"ChargePoint CP_1 connected to websocket.")

            await asyncio.gather(cp.start(), cp.send_boot_notification())

    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Connection closed with error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
