import asyncio
from collections import defaultdict
from typing import Any, Callable


class RealtimeEventHandler:
    # should allow awaitable as well
    event_handlers: dict[str, list[Callable]]
    next_event_handlers: dict[str, list[Callable]]

    def __init__(self) -> None:
        """Initialize the event handler with empty dictionaries for event handlers."""
        self.clear_event_handlers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(" f"\n\t{self.event_handlers=}, " f"\n\t{self.next_event_handlers=}\n)"

    def clear_event_handlers(self) -> bool:
        """
        Clear all event handlers.

        This method resets the `event_handlers` and `next_event_handlers` attributes
        to empty default dictionaries with lists as the default factory.

        Returns:
            bool: Always returns True to indicate the handlers have been cleared.
        """
        self.event_handlers = defaultdict(list)
        self.next_event_handlers = defaultdict(list)
        return True

    def _handler_append(self, handler: dict, callback: Callable) -> Callable:
        handler.append(callback)
        return callback

    def _handler_remove(self, handler: dict, event_name: str, callback: Callable = None):
        """
        Remove event listeners.

        Args:
            handler (dict): The dictionary containing event listeners.
            event_name (str): The name of the event.
            callback (Callable, optional): The specific callback to remove. If None, all callbacks for the event are removed.

        Returns:
            bool: True if successful.

        Raises:
            ValueError: If no listeners are found for the given event name.
        """
        if not (events := handler.get(event_name)):
            _name = f"{handler=}".split("=")[0]
            raise ValueError(f"Could not turn off {_name} for {event_name}. No listeners")

        if callback and (callback in events):
            idx = events.index(callback)
            _ = events.pop(idx)
        else:
            events.clear()

        return True

    def on(self, event_name: str, callback: Callable) -> Callable:
        """
        Register a callback to listen to a specific event.

        This method allows you to register a callback function that will be called
        whenever the specified event is triggered. The callback function will receive
        the event data as its argument.

        Args:
            event_name (str): The name of the event to listen to.
            callback (Callable): The function to call when the event occurs.

        Returns:
            Callable: The callback function.
        """
        return self._handler_append(self.event_handlers[event_name], callback)

    def on_next(self, event_name: str, callback: Callable) -> Callable:
        """
        Register a callback to listen for the next occurrence of a specific event.

        Args:
            event_name (str): The name of the event to listen to.
            callback (Callable): The function to call when the event occurs.

        Returns:
            Callable: The callback function.
        """
        return self._handler_append(self.next_event_handlers[event_name], callback)

    def off(self, event_name: str, callback: Callable = None):
        """
        Remove a callback from the event listeners.

        Args:
            event_name (str): The name of the event.
            callback (Callable, optional): The specific callback to remove. If None, all callbacks for the event are removed.

        Returns:
            bool: True if successful.

        Raises:
            ValueError: If no listeners are found for the given event name.
        """
        return self._handler_remove(self.event_handlers, event_name, callback)

    def off_next(self, event_name: str, callback: Callable = None) -> bool:
        """
        Remove a callback from the next event listeners.

        Args:
            event_name (str): The name of the event.
            callback (Callable, optional): The specific callback to remove. If None, all callbacks for the event are removed.

        Returns:
            bool: True if successful.

        Raises:
            ValueError: If no listeners are found for the given event name.
        """
        return self._handler_remove(self.next_event_handlers, event_name, callback)

    async def wait_for_next(self, event_name: str, timeout: int = None):
        """
        Wait for the next occurrence of a specific event.

        Args:
            event_name (str): The name of the event to wait for.
            timeout (int, optional): The maximum time to wait for the event. Defaults to None.

        Returns:
            Any: The event data if the event occurs within the timeout period, otherwise None.

        Raises:
            TimeoutError: If the event does not occur within the timeout period.
            Exception: If any other exception occurs during the wait.
        """
        event = asyncio.Event()
        result = {}

        def callback(event_data):
            result["data"] = event_data
            event.set()

        self.on_next(event_name, callback)
        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
            next_event = result.get("data")
        except TimeoutError:
            next_event = None
        except Exception as err:
            raise err
        return next_event

    async def dispatch(self, event_name: str, event: Any) -> bool:
        """
        Execute all callbacks associated with an event.

        Args:
            event_name (str): The name of the event to dispatch.
            event (Any): The event data.

        Returns:
            bool: True if successful.
        """
        async def _handle(fns: list[Callable]):
            for fn in fns:
                _ = await fn(event) if asyncio.iscoroutinefunction(fn) else fn(event)

        if handlers := self.event_handlers[event_name]:
            await _handle(handlers)
            handlers.clear()

        if next_handlers := self.next_event_handlers[event_name]:
            await _handle(next_handlers)
            next_handlers.clear()

        return True
