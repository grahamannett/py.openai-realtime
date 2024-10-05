from dataclasses import dataclass

from ..base import RealtimeEvent


@dataclass
class MessageDelta(RealtimeEvent):
    delta: dict
    type: str = "message_delta"


@dataclass
class MessageStart(RealtimeEvent):
    message: dict
    type: str = "message_start"


@dataclass
class MessageStop(RealtimeEvent):
    message: dict
    type: str = "message_stop"
