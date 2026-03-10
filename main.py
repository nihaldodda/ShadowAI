# main.py

import random
import time
import re
import threading
import os
import queue

from listener import listen
from speaker import speak
from commands import execute

from shadow_gui import show_shadow, hide_shadow, app, update_user

from memory_manager import get_name


WAKE_WORDS = ["shadow", "arise", "shadow arise"]

STOP_PHRASES = [
    "shadow rest",
    "shadow deactivate",
    "stand down shadow",
    "shadow standby"
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


active = False
running = True

command_queue = queue.Queue()


# ==============================
# LISTENER THREAD
# ==============================

def listener_loop():

    global running

    while running:

        text = listen()

        if text:
            command_queue.put(text)


# ==============================
# EXECUTION LOOP
# ==============================

def execution_loop():

    global active, running

    while running:

        try:

            command = command_queue.get()

            heard = normalize(command)

            print(f"[DEBUG] Clean: '{heard}'")


            # TERMINATE
            if any(stop in heard for stop in STOP_PHRASES):

                speak(random.choice(SHUTDOWN_RESPONSES))

                hide_shadow()

                time.sleep(1)

                running = False

                os._exit(0)


            # WAKE SYSTEM
            if not active and any(wake in heard for wake in WAKE_WORDS):

                speak(random.choice(WAKE_RESPONSES))

                active = True

                show_shadow()

                name = get_name()

                if name:
                    update_user(name)

                continue


            # EXECUTE COMMAND
            if active:

                execute(heard)

        except Exception as e:

            print("Execution Error:", e)


# ==============================
# START SYSTEM
# ==============================

if __name__ == "__main__":

    threading.Thread(target=listener_loop, daemon=True).start()

    threading.Thread(target=execution_loop, daemon=True).start()

    app.exec()