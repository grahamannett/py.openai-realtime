import asyncio

import pytest

from pyoai_realtime.event_handler import RealtimeEventHandler
from pyoai_realtime.realtime_events import RealtimeEvent, Registry


@pytest.fixture
def event_handler():
    """Fixture to initialize and clear the RealtimeEventHandler before each test."""
    handler = RealtimeEventHandler()
    yield handler


@pytest.mark.asyncio
class TestRealtimeEventHandler:
    async def test_on_and_dispatch(self, event_handler):
        """Test registering event listeners and dispatching events."""
        received_events = []

        def on_event(event):
            received_events.append(event)

        event_handler.on("test_event", on_event)
        await event_handler.dispatch("test_event", {"data": 123})

        assert received_events == [{"data": 123}]

    async def test_on_next_and_wait_for_next(self, event_handler):
        """Test the on_next listener and wait_for_next method."""
        testdata = {"data": 456}

        async def emit_event():
            await asyncio.sleep(0.1)
            await event_handler.dispatch("test_event", testdata)

        asyncio.create_task(emit_event())
        event = await event_handler.wait_for_next("test_event", timeout=1)

        assert event == testdata

    async def test_wait_for_next_timeout(self, event_handler):
        """Test wait_for_next method with a timeout."""
        event = await event_handler.wait_for_next("nonexistent_event", timeout=0.5)
        assert event is None

    async def test_off_event_handler(self, event_handler):
        """Test removing event listeners."""
        received_events = []

        def on_event(event):
            received_events.append(event)

        event_handler.on("test_event", on_event)
        event_handler.off("test_event", on_event)
        await event_handler.dispatch("test_event", {"data": 789})

        assert received_events == []

    async def test_off_all_event_handlers(self, event_handler):
        """Test removing all listeners for an event."""
        received_events = []

        def on_event1(event):
            received_events.append(event)

        def on_event2(event):
            received_events.append(event)

        event_handler.on("test_event", on_event1)
        event_handler.on("test_event", on_event2)
        event_handler.off("test_event")  # Remove all listeners
        await event_handler.dispatch("test_event", {"data": 101112})

        assert received_events == []

    async def test_dispatch_with_no_handlers(self, event_handler):
        """Test dispatching an event that has no handlers."""
        # Should not raise any exceptions
        result = await event_handler.dispatch("no_handler_event", {"data": "no handlers"})
        assert result is True  # Based on dispatch method's return value

    async def test_on_next_event_handler_called_once(self, event_handler):
        """Test that on_next handlers are called only once."""
        received_events = []

        def on_next_event(event):
            received_events.append(event)

        event_handler.on_next("test_event", on_next_event)
        await event_handler.dispatch("test_event", {"data": 1})
        await event_handler.dispatch("test_event", {"data": 2})

        assert received_events == [{"data": 1}]  # Only the first event should be received

    async def test_multiple_handlers(self, event_handler):
        """Test registering multiple handlers for the same event."""
        received_events1 = []
        received_events2 = []

        def on_event1(event):
            received_events1.append(event)

        def on_event2(event):
            received_events2.append(event)

        event_handler.on("test_event", on_event1)
        event_handler.on("test_event", on_event2)
        await event_handler.dispatch("test_event", {"data": "multi"})

        assert received_events1 == [{"data": "multi"}]
        assert received_events2 == [{"data": "multi"}]

    async def test_handler_removal_error(self, event_handler):
        """Test that removing a non-existent handler raises a ValueError."""
        with pytest.raises(ValueError) as exc_info:
            event_handler.off("test_event", lambda x: x)
        assert "Could not turn off" in str(exc_info.value)


@pytest.mark.asyncio
class TestRealtimeEvent:
    async def test_realtime_event_init(self):
        """Test registering event listeners and dispatching events."""

        convo_item_create_data = {
            "event_id": "event_345",
            # "type": "conversation.item.create",
            "type": "conversation.item.create",
            "previous_item_id": None,
            "item": {
                "id": "msg_001",
                "type": "message",
                "status": "completed",
                "role": "user",
                "content": [{"type": "input_text", "text": "Hello, how are you?"}],
            },
        }

        data = convo_item_create_data
        event1 = Registry.factory(data)

        assert event1.item["id"] == "msg_001"

        data["item"]["id"] = "msg_002"
        event2 = Registry[data](**data)
        assert event1.item["id"] == "msg_001"
