import asyncio
import json
import os

from pyoai_realtime import log
from pyoai_realtime.realtime_conversation import RealtimeRelay


async def type_handler(msg):
    if msg["type"] == "test":
        return {"received": "done"}


async def test_action_handler(obj):
    log.info(f"got message, {obj=}")
    return {"received": "done"}


# add handlers by type
handlers_by_type = {"test": test_action_handler}


# add handlers with single func
async def relay_handler(websocket):
    async for message in websocket:
        msg = json.loads(message)

        if msg["type"] in handlers_by_type:
            msg = await handlers_by_type[msg["type"]](msg)

        message = json.dumps(msg)
        await websocket.send(message)


async def main():
    hostname, port = "localhost", int(os.environe.get("RELAY_SERVER_PORT", 8081))
    log.log("running websocket server at=> wss://{hostname}:{port}")
    relay_server = RealtimeRelay(hostname=hostname, port=port)

    await relay_server.run(relay_handler)


if __name__ == "__main__":
    asyncio.run(main())
