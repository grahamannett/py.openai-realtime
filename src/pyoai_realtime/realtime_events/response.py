from dataclasses import dataclass

from pyoai_realtime.realtime_events import RealtimeEvent

# -----
# Client Events


@dataclass
class Cancel(RealtimeEvent):
    conversation_id: str
    type: str = "response.cancel"


@dataclass
class Create(RealtimeEvent):
    conversation_id: str
    response: dict = None
    type: str = "response.create"


# -----
# Server Events
