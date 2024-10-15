from dataclasses import dataclass

from pyoai_realtime.realtime_events.base import RealtimeEvent

# -----
# Client Events


@dataclass
class Cancel(RealtimeEvent):
    type = "response.cancel"
    conversation_id: str


@dataclass
class Create(RealtimeEvent):
    type = "response.create"
    conversation_id: str
    response: dict = None


# -----
# Server Events


@dataclass
class Created(RealtimeEvent):
    type = "response.created"
    response: dict = None


@dataclass
class Done(RealtimeEvent):
    type = "response.done"
    response: dict = None


@dataclass
class OutputItemAdded(RealtimeEvent):
    type = "response.output_item.added"
    response_id: str
    output_index: int
    item: dict = None


@dataclass
class OutputItemDone(RealtimeEvent):
    type = "response.output_item.done"
    response_id: str
    output_index: int
    item: dict = None


@dataclass
class ContentPartAdded(RealtimeEvent):
    type = "response.content_part.added"
    response_id: str
    item_id: str
    output_index: int
    content_index: int
    part: dict = None


@dataclass
class ContentPartDone(RealtimeEvent):
    type = "response.content_part.done"
    response_id: str
    item_id: str
    output_index: int
    content_index: int
    part: dict = None


@dataclass
class TextDelta(RealtimeEvent):
    type = "response.text.delta"
    response_id: str
    item_id: str
    output_index: int
    content_index: int
    delta: str


@dataclass
class TextDone(RealtimeEvent):
    type = "response.text.done"
    response_id: str
    item_id: str
    output_index: int
    content_index: int
    text: str


@dataclass
class AudioTranscriptDelta(RealtimeEvent):
    type = "response.audio_transcript.delta"
    response_id: str
    item_id: str
    output_index: int
    content_index: int
    delta: str


@dataclass
class AudioTranscriptDone(RealtimeEvent):
    type = "response.audio_transcript.done"
    response_id: str
    item_id: str
    output_index: int
    content_index: int
    transcript: str


@dataclass
class AudioDelta(RealtimeEvent):
    type = "response.audio.delta"
    response_id: str
    item_id: str
    output_index: int
    content_index: int
    delta: str


@dataclass
class AudioDone(RealtimeEvent):
    type = "response.audio.done"
    response_id: str
    item_id: str
    output_index: int
    content_index: int


@dataclass
class FunctionCallArgumentsDelta(RealtimeEvent):
    type = "response.function_call_arguments.delta"
    response_id: str
    item_id: str
    output_index: int
    call_id: str
    delta: str


@dataclass
class FunctionCallArgumentsDone(RealtimeEvent):
    type = "response.function_call_arguments.done"
    response_id: str
    item_id: str
    output_index: int
    call_id: str
    arguments: str
