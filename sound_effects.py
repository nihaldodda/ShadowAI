from playsound import playsound
import threading
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SYSTEM_SOUND = os.path.join(BASE_DIR, "system.wav")
XP_SOUND = os.path.join(BASE_DIR, "xp.wav")
LEVELUP_SOUND = os.path.join(BASE_DIR, "levelup.wav")


def play_sound(path):
    def run():
        try:
            playsound(path)
        except:
            pass

    threading.Thread(target=run, daemon=True).start()


def system_notification():
    play_sound(SYSTEM_SOUND)


def xp_gain():
    play_sound(XP_SOUND)


def level_up():
    play_sound(LEVELUP_SOUND)