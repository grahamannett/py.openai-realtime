from dataclasses import dataclass


@dataclass
class RealtimeEvent:
    event_id: str
    type: str


# -----
# Server Events


@dataclass
class Error(RealtimeEvent):
    error: dict
    type: str = "error"
