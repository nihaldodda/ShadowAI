"""Wake / shutdown phrases and text normalization for the voice loop."""
import re

WAKE_WORDS = ["shadow", "arise", "shadow arise"]

STOP_PHRASES = [
    "shadow rest",
    "shadow deactivate",
    "stand down shadow",
    "shadow standby",
]


WAKE_RESPONSES = [

    "Shadow system initialized. Awaiting your command.",
    "Awakening complete. Shadow is online.",
    "All systems bow to your will.",
    "Authority confirmed. Shadow has arisen."

]

SHUTDOWN_RESPONSES = [

    "Returning to the shadows.",
    "System entering standby.",
    "Shutting down."

]


def normalize(text: str):

    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()
