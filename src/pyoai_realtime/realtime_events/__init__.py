from pyoai_realtime.realtime_events import (
    conversation_events,
    input_audio_buffer_events,
    response_events,
    session_events,
)
from pyoai_realtime.realtime_events.base import RealtimeEvent, RealtimeEventRegistry

Registry = RealtimeEventRegistry()
Registry.Conversation = conversation_events
Registry.InputAudioBuffer = input_audio_buffer_events
Registry.Response = response_events
Registry.Session = session_events
