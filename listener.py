# listener.py

import speech_recognition as sr
import time
from speaker import is_speaking

recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen():

    # HARD BLOCK while speaking
    if is_speaking:
        return None

    with mic as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            return text.lower()

        except:
            return None