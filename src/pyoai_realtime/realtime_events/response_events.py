from dataclasses import dataclass, field

from pyoai_realtime.realtime_events.base import RealtimeEvent

# -----
# Client Events


@dataclass
class Cancel(RealtimeEvent):
    conversation_id: str
    type = "response.cancel"


@dataclass
class Create(RealtimeEvent):
    conversation_id: str
    response: dict = field(default=None)
    type = "response.create"


# -----
# Server Events
