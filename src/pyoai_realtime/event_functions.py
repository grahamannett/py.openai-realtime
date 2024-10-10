from array import array

from pyoai_realtime.realtime_events import conversation_events


class ConversationInterface:
    item_lookup: dict
    items: list
    response_lookup: dict
    responses: list
    queued_speech_items: dict
    queued_transcript_items: dict
    queued_input_audio: list[int] | array

    def __init__(self):
        self.clear()

    def clear(self):
        """Clear the conversation history."""
        self.item_lookup = {}
        self.items = []
        self.response_lookup = {}
        self.responses = []
        self.queued_speech_items = {}
        self.queued_transcript_items = {}
        self.queued_input_audio = None


class EventFunctionsMixin:
    conversation: ConversationInterface
    event_processor: dict[str, callable]
    default_frequency: int

    def _attach_events(self):
        self.event_processor[conversation_events.Created.type] = self._conversation_item_created
        self.event_processor[conversation_events.Truncated.type] = self._converstaion_item_truncated

    def _conversation_item_created(self, event: conversation_events.Created):
        new_item = event.item
        convo: ConversationInterface = self.conversation

        if new_item.id not in convo.item_lookup:
            convo.item_lookup[new_item.id] = new_item
            convo.items.append(new_item)

        new_item["formatted"] = {
            "audio": [],
            "text": "",
            "transcript": "",
        }

        if new_item.id in convo.queued_speech_items:
            new_item["formatted"]["audio"] = convo.queued_speech_items[new_item.id]["audio"]
            _ = convo.queued_speech_items.pop(new_item.id)

        if "content" in new_item:
            text_content = [c["type"] in ["text", "input_text"] for c in new_item["content"]]

            for content in text_content:
                new_item["formatted"]["text"] += content["text"]

        if new_item.id in convo.queued_transcript_items:
            new_item["formatted"]["transcript"] = convo.queued_transcript_items["transcript"]
            _ = convo.queued_transcript_items.pop(new_item.id)

        if new_item["type"] == "message":
            if new_item["role"] == "user":
                new_item["status"] = "completed"
                if convo.queued_input_audio:
                    new_item["formatted"]["audio"] = convo.queued_input_audio
                    convo.queued_input_audio = None
            else:
                new_item["status"] = "in_progress"
        elif new_item["type"] == "function_call":
            new_item["formatted"]["tool"] = {
                "name": new_item["name"],
                "type": "function",
                "call_id": new_item["call_id"],
                "arguments": "",
            }
            new_item["status"] = "in_progress"
        elif new_item["type"] == "function_call_output":
            new_item["status"] = "completed"
            new_item["formatted"]["output"] = new_item["output"]
        return {"item": new_item, "delta": None}

    def _converstaion_item_truncated(self, event: conversation_events.Truncated):
        item_id = event.item_id
        audio_end_ms = event.audio_end_ms

        convo: ConversationInterface = self.conversation

        if (item := convo.item_lookup.get(item_id)) is None:
            raise ValueError(f"item.truncated: Item {item_id} not found")

        end_index = (audio_end_ms * self.default_frequency) / 1000
        item["formatted"]["transcript"] = ""
        item["formatted"]["audio"] = item["formatted"]["audio"][:end_index]
        return {"item": item, "delta": None}

    def _conversation_item_deleted(self, event: conversation_events.Deleted):
        item_id = event.item_id
        convo: ConversationInterface = self.conversation

        if (item := convo.item_lookup.get(item_id)) is None:
            raise ValueError(f"item.deleted: Item {item_id} not found")

        _ = convo.item_lookup.pop(item_id)

        # the js code does this (slice with nothing)
        # index = convo.items.index(item)
        # if index > -1:
        #     convo.items[index, 1]

        return {"item": item, "delta": None}
