"""Input audio buffer module for realtime events."""

from dataclasses import dataclass

from pyoai_realtime.realtime_events.base import RealtimeEvent

# -----
# Client Events


@dataclass
class Append(RealtimeEvent):
    audio: bytes  # docs say `"audio": "Base64EncodedAudioData"`
    type = "input_audio_buffer.append"


@dataclass
class Clear(RealtimeEvent):
    type = "input_audio_buffer.clear"


@dataclass
class Commit(RealtimeEvent):
    type = "input_audio_buffer.commit"


# -----
# Server Events


@dataclass
class Committed(RealtimeEvent):
    previous_item_id: str
    item_id: str
    type = "input_audio_buffer.committed"


@dataclass
class Cleared(RealtimeEvent):
    type: str = "input_audio_buffer.cleared"


@dataclass
class SpeechStarted(RealtimeEvent):
    audio_start_ms: int
    item_id: str
    type = "input_audio_buffer.speech_started"


@dataclass
class SpeechStopped(RealtimeEvent):
    audio_end_ms: int
    item_id: str
    type = "input_audio_buffer.speech_stopped"
