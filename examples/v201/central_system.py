import asyncio
import logging
from datetime import datetime

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package. Please install it by running:")
    print()
    print(" $ pip install websockets")
    import sys
    sys.exit(1)

from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call_result

# Set logging level to INFO to reduce verbosity
logging.basicConfig(level=logging.INFO)

class ChargePoint(cp):
    @on("BootNotification")
    def on_boot_notification(self, charging_station, reason, **kwargs):
        model = charging_station.get('model', 'Unknown Model')
        vendor_name = charging_station.get('vendor_name', 'Unknown Vendor')
        logging.info(f"Boot Notification from {model} ({vendor_name})")

        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(), interval=10, status="Accepted"
        )

    @on("Heartbeat")
    def on_heartbeat(self):
        logging.info("Received Heartbeat")
        return call_result.Heartbeat(
            current_time=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        )

async def on_connect(websocket, path):
    """For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    requested_protocols = websocket.request_headers.get("Sec-WebSocket-Protocol")
    if requested_protocols:
        logging.info(f"Protocols Matched: {websocket.subprotocol}")
    else:
        logging.warning("Client hasn't requested any Subprotocol. Closing Connection")
        return await websocket.close()

    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        logging.warning(
            "Protocols Mismatched | Expected Subprotocols: %s,"
            " but client supports %s | Closing connection",
            websocket.available_subprotocols,
            requested_protocols,
        )
        return await websocket.close()

    charge_point_id = path.strip("/")
    charge_point = ChargePoint(charge_point_id, websocket)

    await charge_point.start()

async def main():
    server = await websockets.serve(
        on_connect, "0.0.0.0", 9000, subprotocols=["ocpp2.0.1"]
    )

    logging.info("Central System Started listening to new connections...")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
