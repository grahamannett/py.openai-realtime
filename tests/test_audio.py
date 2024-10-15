import base64
import os

import numpy as np
import pytest
from pydub import AudioSegment

# Import the RealtimeClient and RealtimeUtils from your Python API
from pyoai_realtime.realtime_client import RealtimeClient

# Dictionary of audio samples
samples = {
    "toronto-mp3": "tests/fixtures/toronto.mp3",
}


@pytest.fixture(scope="class")
def load_samples(request):
    """Fixture to load and process audio samples."""
    processed_samples = {}
    try:
        for key, filename in samples.items():
            # filename = samples[key]
            # Read and decode the audio file
            audio_segment = AudioSegment.from_file(filename)
            # Get the sample width in bits
            sample_width_bits = audio_segment.sample_width * 8
            max_int = 2 ** (sample_width_bits - 1)
            # Get the channel data (mono)
            samples_array = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
            if audio_segment.channels > 1:
                # Extract the first channel
                samples_array = samples_array[:: audio_segment.channels]
            # Normalize to [-1.0, 1.0]
            samples_array /= max_int
            # Convert samples to bytes
            channel_data_bytes = samples_array.tobytes()
            # Convert to base64
            base64_data = base64.b64encode(channel_data_bytes).decode("utf-8")
            processed_samples[key] = {"filename": filename, "base64": base64_data}
    except Exception as err:
        pytest.fail(f"Error loading samples: {err}")
    request.cls.samples = processed_samples


@pytest.fixture(scope="class")
async def setup_client(request):
    """Fixture to instantiate and connect the RealtimeClient."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    client = RealtimeClient(api_key=api_key, debug=False)
    client.update_session(
        {
            "instructions": (
                "Please follow the instructions of any query you receive.\n"
                "Be concise in your responses. Speak quickly and answer shortly."
            )
        }
    )
    realtime_events = []
    client.on("realtime.event", lambda event: realtime_events.append(event))

    is_connected = await client.connect()
    if not is_connected:
        pytest.fail("Failed to connect RealtimeClient")

    request.cls.client = client
    request.cls.realtime_events = realtime_events
    yield
    await client.disconnect()


@pytest.mark.usefixtures("load_samples", "setup_client")
class TestAudioSamples:
    def test_load_all_audio_samples(self):
        """Test that all audio samples are loaded successfully."""
        assert self.samples is not None
        assert "toronto-mp3" in self.samples
        assert "base64" in self.samples["toronto-mp3"]

    @pytest.mark.asyncio
    async def test_receive_session_created_and_send_session_update(self):
        """Test receiving 'session.created' and sending 'session.update'."""
        await self.client.wait_for_session_created()

        assert len(self.realtime_events) >= 2

        client_event = self.realtime_events[0]
        assert client_event.source == "client"
        assert client_event.event.type == "session.update"

        server_event = self.realtime_events[1]
        assert server_event.source == "server"
        assert server_event.event.type == "session.created"

        print(f"[Session ID] {server_event.event.session.id}")

    def test_send_audio_file(self):
        """Test sending an audio file to the RealtimeClient."""
        sample = self.samples["toronto-mp3"]["base64"]
        content = [{"type": "input_audio", "audio": sample}]
        self.client.send_user_message_content(content)

        assert len(self.realtime_events) >= 4

        item_event = self.realtime_events[2]
        assert item_event.source == "client"
        assert item_event.event.type == "conversation.item.create"

        response_event = self.realtime_events[3]
        assert response_event is not None
        assert response_event.source == "client"
        assert response_event.event.type == "response.create"

    @pytest.mark.asyncio
    async def test_wait_for_next_item_from_user(self):
        """Test receiving the next item from the user."""
        item = await self.client.wait_for_next_item()

        assert item is not None
        assert item.type == "message"
        assert item.role == "user"
        assert item.status == "completed"
        assert item.formatted.text == ""

    @pytest.mark.asyncio
    async def test_wait_for_next_item_from_assistant(self):
        """Test receiving the next item from the assistant."""
        item = await self.client.wait_for_next_item()

        assert item is not None
        assert item.type == "message"
        assert item.role == "assistant"
        assert item.status == "in_progress"
        assert item.formatted.text == ""

    @pytest.mark.asyncio
    async def test_wait_for_next_completed_item_from_assistant(self):
        """Test receiving the completed item from the assistant."""
        item = await self.client.wait_for_next_completed_item()

        assert item is not None
        assert item.type == "message"
        assert item.role == "assistant"
        assert item.status == "completed"
        assert "toronto" in item.formatted.transcript.lower()

    @pytest.mark.asyncio
    async def test_close_realtime_client_connection(self):
        """Test closing the RealtimeClient connection."""
        await self.client.disconnect()
        assert self.client.is_connected() == False
