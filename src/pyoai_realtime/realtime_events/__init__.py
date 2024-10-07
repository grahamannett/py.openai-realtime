from copy import deepcopy

from pyoai_realtime.realtime_events.base import RealtimeEvent, RealtimeEventRegistry
from pyoai_realtime.realtime_events import conversation
from pyoai_realtime.realtime_events import input_audio_buffer
from pyoai_realtime.realtime_events import response


Registry = RealtimeEventRegistry()
Registry.Conversation = conversation
Registry.InputAudioBuffer = input_audio_buffer
Registry.Response = response
