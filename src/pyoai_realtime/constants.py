import os

DEFAULT_MODEL = "gpt-4o-realtime-preview-2024-10-01"
DEFAULT_URL = "wss://api.openai.com/v1/realtime"


# CAN OVERWRITE THESE IN YOUR ENVIRONMENT
DEBUG = os.environ.get("DEBUG", False)

# related to relay server
PORT = int(os.environ.get("PORT", 8081))
HOSTNAME = os.environ.get("HOSTNAME", "localhost")
