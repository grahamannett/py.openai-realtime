from dataclasses import dataclass, field

from pyoai_realtime.realtime_events.base import RealtimeEvent


@dataclass
class Update(RealtimeEvent):
    # https://platform.openai.com/docs/api-reference/realtime-client-events/session/update
    session: dict = field(default_factory=dict)
    type: str = "session.update"
