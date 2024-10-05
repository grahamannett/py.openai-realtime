from dataclasses import dataclass

from pyoai_realtime.realtime_events import RealtimeEvent


@dataclass
class Append(RealtimeEvent):
    audio: bytes  # docs say `"audio": "Base64EncodedAudioData"`
    type: str = "input_audio_buffer.append"


@dataclass
class Clear(RealtimeEvent):
    type: str = "input_audio_buffer.clear"


@dataclass
class Commit(RealtimeEvent):
    type: str = "input_audio_buffer.commit"
