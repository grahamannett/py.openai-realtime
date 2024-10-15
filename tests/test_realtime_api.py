import asyncio
import os

import pytest

from pyoai_realtime.realtime_api import DEFAULT_MODEL, DEFAULT_URL, RealtimeAPI


@pytest.fixture
def api_key():
    return os.environ.get("OPENAI_API_KEY")


@pytest.mark.asyncio
class TestRealtimeAPI:
    async def test_instantiate_without_api_key(self):
        """Test instantiating RealtimeAPI without an API key."""
        realtime = RealtimeAPI()
        assert realtime is not None
        assert realtime.api_key is None
        assert realtime.url == DEFAULT_URL

    async def test_instantiate_with_custom_url(self):
        """Test instantiating RealtimeAPI with a custom URL."""
        custom_url = "wss://custom.api.com/v1/realtime"
        realtime = RealtimeAPI(url=custom_url)
        assert realtime.url == custom_url

    async def test_connect_without_api_key(self):
        """Test connecting to RealtimeAPI without an API key."""
        realtime = RealtimeAPI()

        with pytest.raises(Exception) as exc_info:
            await realtime.connect()

        assert "Could not connect" in str(exc_info.value)

    async def test_instantiate_with_api_key(self, api_key):
        """Test instantiating RealtimeAPI with an API key."""
        realtime = RealtimeAPI(api_key=api_key)
        assert realtime is not None
        assert realtime.api_key == api_key

    async def test_connect_with_api_key(self, api_key):
        """Test connecting to RealtimeAPI with a valid API key."""
        realtime = RealtimeAPI(api_key=api_key)
        connected = await realtime.connect()
        assert connected is True
        assert realtime.connected is True
        print(f"ws-state: {realtime.ws.state}")
        await realtime.ws.close()
        print(f"ws-state: {realtime.ws.state}")
        # breakpoint()
        # await realtime.disconnect()

    async def test_connect_and_session_created(self, api_key):
        realtime = RealtimeAPI(api_key=api_key)
        received_events = {}

        async def _fn1(event):
            received_events[event["event_id"]] = event

        async def _fn2(event):
            assert received_events != {}

        async def _fn3(event):
            received_events["session.updated"] = event

        realtime.on_next("server.session.created", _fn1)
        realtime.on_next("server.session.created", _fn2)
        realtime.on("server.session.updated", _fn3)

        connected = await realtime.connect()
        assert connected is True
        assert realtime.connected is True

        await realtime.send("session.update", {"session": {"modalities": ["text"]}})
        await asyncio.sleep(0.1)

        assert "session.updated" in received_events

        await realtime.disconnect()

    async def test_connect_with_custom_model(self, api_key):
        """Test connecting to RealtimeAPI with a custom model."""
        realtime = RealtimeAPI(api_key=api_key)
        custom_model = "custom-model-2024"
        connected = await realtime.connect(model=custom_model)
        assert connected is True
        assert realtime.connected is True
        await realtime.disconnect()

    async def test_disconnect(self, api_key):
        """Test disconnecting from RealtimeAPI."""
        realtime = RealtimeAPI(api_key=api_key)
        await realtime.connect()
        assert realtime.connected is True

        disconnected = await realtime.disconnect()
        assert disconnected is True
        assert realtime.connected is False

    async def test_send_message(self, api_key):
        """Test sending a message through RealtimeAPI."""
        realtime = RealtimeAPI(api_key=api_key)
        await realtime.connect()

        event_name = "test_event"
        data = {"message": "Hello, World!"}
        sent = await realtime.send(event_name, data)
        assert sent is True

        await realtime.disconnect()

    async def test_receive_message(self, api_key):
        """Test receiving a message through RealtimeAPI."""
        realtime = RealtimeAPI(api_key=api_key)
        await realtime.connect()

        # Mock receiving a message
        event_name = "test_event"
        event_data = {"type": event_name, "message": "Hello, World!"}
        received = realtime.receive(event_name, event_data)
        assert received is True

        await realtime.disconnect()

    @pytest.fixture(autouse=True)
    async def teardown(self):
        """Ensure disconnection after each test."""
        yield
        # This is not needed anymore as we're disconnecting in each test
        # But we can keep it as an extra precaution
        for task in asyncio.all_tasks():
            if not task.done():
                task.cancel()
