from dataclasses import dataclass

from pyoai_realtime.realtime_events.base import RealtimeEvent

# -----
# Server Events


@dataclass
class Error(RealtimeEvent):
    """
    Represents an error event in the PyOAI Realtime system.

    https://platform.openai.com/docs/api-reference/realtime-server-events/error

    This class extends RealtimeEvent to provide specific error information
    when something goes wrong during the realtime communication.

    Attributes:
        error (dict): A dictionary containing error details.
        type (str): The type of the event, always set to "error" for this class.
    """

    type = "error"

    error: dict = None


@dataclass
class RateLimitsUpdated(RealtimeEvent):
    """
    Represents a rate limits updated event in the PyOAI Realtime system.

    https://platform.openai.com/docs/api-reference/realtime-server-events/rate_limits_updated

    This class extends RealtimeEvent to provide information about the rate
    limits for the OpenAI API.

    Attributes:
        rate_limits (dict): A dictionary containing rate limit details.
        type (str): The type of the event, always set to "rate_limits_updated" for this class.
    """

    type = "rate_limits_updated"

    rate_limits: list[dict] = None
