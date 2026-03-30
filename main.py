# main.py

import random
import time
import re
import threading
import os
import queue

from shadow.voice.listener import listen
from shadow.voice.speaker import speak
from shadow.core.commands import execute

from shadow.ui.shadow_gui import (
    show_shadow,
    hide_shadow,
    app,
    update_user,
    notify_listening,
    notify_processing,
)

from shadow.systems.profile_system import get_name

from shadow.voice.wakeword import (
    WAKE_WORDS,
    STOP_PHRASES,
    WAKE_RESPONSES,
    SHUTDOWN_RESPONSES,
    normalize,
)


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

                notify_processing(True)
                try:
                    execute(heard)
                finally:
                    notify_processing(False)

        except Exception as e:

            print("Execution Error:", e)


# ==============================
# START SYSTEM
# ==============================

if __name__ == "__main__":

    threading.Thread(target=listener_loop, daemon=True).start()

    threading.Thread(target=execution_loop, daemon=True).start()

    app.exec()
