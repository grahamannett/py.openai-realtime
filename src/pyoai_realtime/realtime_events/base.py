"""Base module for realtime events."""

from copy import deepcopy
from dataclasses import dataclass

_TYPE_FIELD = "type"


@dataclass
class RealtimeEvent:
    """
    Base class for all realtime events in the PyOAI Realtime system.

    This class serves as a foundation for various event types used in the
    realtime communication between the client and the server.

    Attributes:
        event_id (str): A unique identifier for the event.
        type (str): The type of the event, used for event differentiation.
    """

    event_id: str
    type: str

    def __init_subclass__(cls) -> None:
        RealtimeEventRegistry._registry[getattr(cls, _TYPE_FIELD)] = cls


class RealtimeEventRegistry:
    """Registry for realtime events."""

    _registry = {}

    @classmethod
    def factory(cls, event: dict, as_copy: bool = True) -> type[RealtimeEvent]:
        """
        Create a RealtimeEvent instance from a response object

        Args:
            event (dict): The event data.
            as_copy (bool, optional): Whether to create a deep copy of the event. Defaults to True.

        Returns:
            type[RealtimeEvent]: An instance of a RealtimeEvent subclass.
        """
        if as_copy:
            event = deepcopy(event)
        return RealtimeEventRegistry._registry[event[_TYPE_FIELD]](**event)

    def __getitem__(self, event: dict | str) -> RealtimeEvent:
        return RealtimeEventRegistry._registry[event[_TYPE_FIELD]]
