# speaker.py

import subprocess
import threading
import queue
import time

speech_queue = queue.Queue()
is_speaking = False

# Persistent PowerShell TTS
ps = subprocess.Popen(
    ["powershell", "-NoExit", "-Command",
     "Add-Type -AssemblyName System.Speech; "
     "$global:speak = New-Object System.Speech.Synthesis.SpeechSynthesizer;"],
    stdin=subprocess.PIPE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    text=True
)

def speech_worker():
    global is_speaking

    while True:
        text = speech_queue.get()
        if text is None:
            break

        try:
            is_speaking = True
            print("[SPEAKING]:", text)

            safe_text = text.replace("'", "''")
            ps.stdin.write(f"$global:speak.Speak('{safe_text}')\n")
            ps.stdin.flush()

            # Block mic slightly after speaking
            time.sleep(1.2)

        except Exception as e:
            print("Speech Error:", e)

        finally:
            is_speaking = False
            speech_queue.task_done()

threading.Thread(target=speech_worker, daemon=True).start()

def speak(text):
    if text:
        speech_queue.put(text)
