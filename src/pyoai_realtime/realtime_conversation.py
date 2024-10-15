import asyncio
import json
from array import array
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

from websockets.asyncio.server import ServerConnection, serve

from pyoai_realtime.constants import HOSTNAME, PORT
from pyoai_realtime.event_functions import ConversationInterface, EventFunctionsMixin
from pyoai_realtime.realtime_events import RealtimeEvent, conversation_events

HandlerType = Callable[[Any], Awaitable[None]]


class EventProcessor(EventFunctionsMixin):
    def __init__(self, conversation: ConversationInterface):
        self.conversation = conversation

    def __call__(self, event: str):
        pass

    def _response_created(self, event: Any):
        response = event.data
        convo: ConversationInterface = self.conversation
        if response.id not in convo.response_lookup:
            convo.response_lookup[response.id] = response
            convo.responses.append(response)
        return {"item": None, "delta": None}

    def process_event(self, event: RealtimeEvent, data: dict):
        if not event.event_id:
            raise ValueError("Event id is required")
        if not event.type:
            raise ValueError("Event type is required")

        event_class = self.event_processor[event.type]


class RealtimeConversation:
    default_frequency = 24_000  # 24,000 Hz

    def __init__(self):
        self.conversation = ConversationInterface()
        self.conversation.clear()

    def queue_input_audio(self, input_audio):
        self.queued_input_audio = input_audio
        return self.queued_input_audio


class RealtimeRelay:
    def __init__(
        self,
        hostname: str = HOSTNAME,
        port: int = PORT,
        handler: HandlerType = None,
        # not used now but planning for later
        json_func: callable = None,
        send_func: callable = None,
    ):
        self.hostname = hostname
        self.port = port
        self._json_func = json_func
        self._send_func = send_func
        self.handler = handler or self._handler

    async def _default_handler(self, msg: dict) -> dict:
        return msg

    async def _handler(self, websocket: ServerConnection, handler: dict | Callable):
        async def fn(msg):
            # allow for a dict of functions
            fn = handler.get(msg["type"], self._default_handler) if isinstance(handler, dict) else handler

            if asyncio.iscoroutine(out := fn(msg)):
                await out
            return out

        # allow for overriding the message loading/dumping (e.g. for logging/customization)
        msg_load, msg_dump = self._json_func if self._json_func else (json.loads, json.dumps)

        async def _send_func(msg: str):
            return await websocket.send(msg)

        _send_func = self._send_func or _send_func

        async for message in websocket:
            message = msg_load(message)
            message = await fn(message)
            message = msg_dump(message)
            await websocket.send(message)

    async def run(self, handler: HandlerType = None, hostname: str = None, port: int = None, **kwargs):
        handler = handler or self.handler
        hostname = hostname or self.hostname
        port = port or self.port

        server = await serve(handler, hostname, port, **kwargs)
        await server.serve_forever()
