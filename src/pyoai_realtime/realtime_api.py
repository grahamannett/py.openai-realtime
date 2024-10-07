import asyncio
import datetime
import json
from typing import Optional, Any, Dict

import websockets


from pyoai_realtime.event_handler import RealtimeEventHandler
from pyoai_realtime.utils import generate_id

DEFAULT_MODEL = "gpt-4o-realtime-preview-2024-10-01"
DEFAULT_URL = "wss://api.openai.com/v1/realtime"
DEBUG = False


class RealtimeAPI(RealtimeEventHandler):
    debug = DEBUG

    def __init__(
        self,
        url: str = DEFAULT_URL,
        api_key: str = None,
    ):
        super().__init__()
        self.url = url or DEFAULT_URL
        self.api_key = api_key
        self.ws = None

    @property
    def connected(self) -> bool:
        """Check if the WebSocket is connected."""
        return self.ws is not None and not self.ws.closed

    def log(self, *args: Any) -> bool:
        """Log debug information if debug mode is enabled."""
        if self.debug:
            date = datetime.datetime.now().isoformat()
            log_items = [f"[Websocket/{date}]"]
            for arg in args:
                if isinstance(arg, (dict, list)):
                    log_items.append(json.dumps(arg, indent=2))
                else:
                    log_items.append(str(arg))
            print(" ".join(log_items))
        return True

    async def connect(self, model: str = DEFAULT_MODEL) -> bool:
        """
        Connect to the API with the specified model.

        Args:
            model (str): The model to use for the connection. Defaults to DEFAULT_MODEL.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        if not self.api_key and self.url == DEFAULT_URL:
            print(f'No apiKey provided for connection to "{self.url}"')
        if self.connected:
            raise RuntimeError("Already connected")

        url = f"{self.url}?model={model}" if model else self.url
        headers = {"OpenAI-Beta": "realtime=v1"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            self.ws = await websockets.connect(url, extra_headers=headers)
            self.log(f'Connected to "{self.url}"')
            # Start the receive loop
            asyncio.create_task(self._receive_loop())
            return True
        except Exception as e:
            await self.disconnect()
            raise Exception(f'Could not connect to "{self.url}": {str(e)}') from e

    async def _receive_loop(self):
        try:
            async for message in self.ws:
                data = json.loads(message)
                self.receive(data.get("type"), data)
        except websockets.ConnectionClosed as e:
            self.log(f"Connection closed: {e}")
            await self.disconnect()
            self.dispatch("close", {"error": True})
        except Exception as e:
            self.log(f"Error: {e}")
            await self.disconnect()
            self.dispatch("close", {"error": True})

    async def disconnect(self) -> bool:
        """Close the WebSocket connection if it exists."""
        if self.ws:
            await self.ws.close()
            self.ws = None
            self.log(f'Disconnected from "{self.url}"')
        return True

    async def receive(self, event_name: str, event: Dict[str, Any]) -> bool:
        self.log("received:", event_name, event)
        self.dispatch(f"server.{event_name}", event)
        self.dispatch("server.*", event)
        return True

    async def send(self, event_name: str, data: Optional[Dict[str, Any]] = None) -> bool:
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
            raise Exception("RealtimeAPI is not connected")
        data = data or {}
        if not isinstance(data, dict):
            raise Exception("data must be a dictionary")
        event_id = generate_id("evt_")
        event = {"event_id": event_id, "type": event_name}
        event.update(data)
        self.dispatch(f"client.{event_name}", event)
        self.dispatch("client.*", event)
        self.log("sent:", event_name, event)
        await self.ws.send(json.dumps(event))
        return True
