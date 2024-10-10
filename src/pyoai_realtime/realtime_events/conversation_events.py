from dataclasses import dataclass, field

from pyoai_realtime.realtime_events.base import RealtimeEvent

# -----
# Client Events


@dataclass
class Create(RealtimeEvent):
    type = "conversation.item.create"
    previous_item_id: str
    item: dict = None


@dataclass
class Truncate(RealtimeEvent):
    type = "conversation.item.truncate"
    item_id: str
    content_index: int
    audio_end_ms: int


@dataclass
class Delete(RealtimeEvent):
    type = "conversation.item.delete"
    item_id: str


# -----
# Server Events


@dataclass
class Created(RealtimeEvent):
    previous_item_id: str
    type = "conversation.item.created"
    item: dict = field(default=None)


@dataclass
class Completed(RealtimeEvent):
    item_id: str
    content_index: int
    type = "conversation.item.input_audio_transcription.completed"
    transcript: str


@dataclass
class Failed(RealtimeEvent):
    item_id: str
    content_index: int
    type = "conversation.item.input_audio_transcription.failed"
    error: dict = field(default=None)


@dataclass
class Truncated(RealtimeEvent):
    item_id: str
    content_index: int
    type = "conversation.item.truncated"
    audio_end_ms: int


@dataclass
class Deleted(RealtimeEvent):
    type = "conversation.item.deleted"
    item_id: str


# -----
# Factory

# InputAudioTranscription.Completed = Completed


class InputAudioTranscription:
    # from Server events:
    Completed = Completed
    Failed = Failed


class Item:
    # from Client events:
    # https://platform.openai.com/docs/api-reference/realtime-client-events/conversation-item-create
    Create = Create
    Truncate = Truncate
    Delete = Delete

    # from Server events:
    # https://platform.openai.com/docs/api-reference/realtime-server-events/conversation-item-created
    Created = Created
    Truncated = Truncated
    Deleted = Deleted

    # Items here are part of
    # `conversation.item.input_audio_transcription.`
    InputAudioTranscription = InputAudioTranscription


# Item.Create = Create
# Item.Created = Created
