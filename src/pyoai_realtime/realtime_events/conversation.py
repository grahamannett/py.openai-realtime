from dataclasses import dataclass

from pyoai_realtime.realtime_events import RealtimeEvent


class Item:
    pass


# -----
# Client Events


@dataclass
class Create(RealtimeEvent):
    conversation_id: str
    item: dict
    previous_item_id: str = None
    type: str = "conversation.item.create"


# -----
# Server Events


# -----
# Factory


Item.Create = Create
