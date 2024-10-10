import asyncio
import json
from typing import Any, Dict, Optional

import websockets
import websockets.protocol
from websockets.asyncio.client import ClientConnection
from websockets.asyncio.client import connect

from pyoai_realtime.constants import DEBUG, DEFAULT_MODEL, DEFAULT_URL
from pyoai_realtime.event_handler import RealtimeEventHandler
from pyoai_realtime.utils import generate_id
from pyoai_realtime import log


class RealtimeAPI(RealtimeEventHandler):
    """
    RealtimeAPI is a class that provides a WebSocket connection to the OpenAI Realtime API.
    """

    ws: ClientConnection

    def __init__(
        self,
        url: str = DEFAULT_URL,
        api_key: str = None,
        debug: bool = DEBUG,
    ):
        super().__init__()
        self.ws = None
        self.url = url or DEFAULT_URL
        self.api_key = api_key
        self.debug = debug

    @property
    def connected(self) -> bool:
        """Check if the WebSocket is connected."""
        if self.ws:
            return self.ws.state == websockets.protocol.State.OPEN
        return False

    def log(self, *args: Any) -> bool:
        """Log debug information if debug mode is enabled."""
        # return _log(self.debug, *args)
        log.print(*args)
        return True

    def _check_ws_setup(self, url: str, api_key: str, model: str) -> bool:
        if (not api_key) and (url == DEFAULT_URL):
            print(f'No api_key provided for connection to "{url}"')
        if self.connected:
            raise RuntimeError("Already connected")
        return True

    async def connect(self, model: str = DEFAULT_MODEL) -> bool:
        """
        Connect to the API with the specified model.

        Args:
            model (str): The model to use for the connection. Defaults to DEFAULT_MODEL.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        self._check_ws_setup(self.url, self.api_key, model)

        url = f"{self.url}?model={model}" if model else self.url

        headers = {"OpenAI-Beta": "realtime=v1"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        def _done_cb(task):
            print("==> in _done_callback")

        async def _keep_alive(stop_coro):
            await stop_coro

        try:
            self.ws = await connect(url, additional_headers=headers)
            recv_task = asyncio.create_task(self._receive_loop())
            recv_task.add_done_callback(_done_cb)
            # stop_task = asyncio.create_task(_keep_alive(asyncio.get_running_loop().create_future()))

            self.background_tasks["receive_loop"] = recv_task
            # self.background_tasks["stop"] = stop_task

            return True
        except Exception as err:
            raise err

    async def _receive_loop(self):
        async def _err_done():
            await self.disconnect()
            await self.dispatch("close", {"error": True})

        try:
            # while True:
            async for message in self.ws:
                json_data = json.loads(message)
                await self.receive(json_data.get("type"), json_data)

        except websockets.ConnectionClosed as err:
            self.log(f"Connection closed: {err}")
            await _err_done()
        except Exception as err:
            self.log(f"Error: {err}")
            await _err_done()

    async def disconnect(self) -> bool:
        """Close the WebSocket connection if it exists."""
        if self.ws:
            await self.ws.close()
            self.ws = None
            self.log(f'Disconnected from "{self.url}"')
        return True

    async def receive(self, event_name: str, event: Dict[str, Any]) -> bool:
        self.log("RECEIVED:", event_name, event)
        await self.dispatch(f"server.{event_name}", event)
        await self.dispatch("server.*", event)
        return True

    async def send(self, event_name: str, data: Optional[Dict[str, Any]] | None = None) -> bool:
        """Send an event to the server.

        Args:
            event_name (str): Name of the event to send.
            data (Optional[Dict[str, Any]], optional): Data to send with the event. Defaults to None.

        Returns:
            bool: True if the event was sent successfully.

        Raises:
            Exception: If RealtimeAPI is not connected.
        """
        if not self.connected:
            raise RuntimeError("RealtimeAPI is not connected")

        data = data or {}

        event = {**data, "event_id": generate_id("evt_"), "type": event_name}

        await self.dispatch(f"client.{event_name}", event)
        await self.dispatch("client.*", event)
        self.log("SENT:", event_name, event)
        json_data = json.dumps(event)
        await self.ws.send(json_data)
        return True
