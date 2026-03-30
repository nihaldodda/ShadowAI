# commands.py

from shadow.ui.shadow_gui import (
    update_last_command,
    update_level,
    update_quest,
    update_rank,
    update_user,
    update_xp,
)

import datetime
import os

from shadow.voice.listener import listen
from shadow.voice.speaker import is_speaking, speak

from shadow.core.shadow_state import ShadowState
from shadow.systems.quest_system import QuestSystem

from shadow.voice.sound_effects import level_up, system_notification, xp_gain

from shadow.core.intent_model import predict_intent
from shadow.core.learning_manager import add_training_example

from shadow.systems.profile_system import add_goal, get_goals, get_name, set_name

from shadow.automation.browser_automation import (
    close_all_tabs,
    close_specific_tab,
    list_open_tabs,
    open_generic_website,
    switch_to_tab,
)

shadow = ShadowState()
quests = QuestSystem()


# ==============================
# Utility
# ==============================

def tell_time():

    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The time is {now}.")


def shutdown_system():

    speak("Confirm shutdown.")

    confirmation = listen()

    if confirmation and any(word in confirmation for word in ["yes", "confirm", "do it"]):

        speak("Shutting down.")
        os.system("shutdown /s /t 5")

    else:
        speak("Shutdown cancelled.")


# ==============================
# Quest System
# ==============================

def assign_quest(category: str | None = None):
    quest = quests.assign_random_quest() if category is None else quests.assign_category_quest(category)

    if quest:

        system_notification()

        update_quest(quest.title)

        desc = (quest.description or "").strip()
        if desc:
            speak(f"New quest: {quest.title}. {desc}")
        else:
            speak(f"New quest: {quest.title}.")


def complete_quest():

    xp = quests.complete_quest()

    if xp > 0:

        shadow.gain_xp(xp)

        xp_gain()

        speak(f"Quest completed. You gained {xp} experience points.")

        if shadow.just_leveled_up:

            level_up()

            speak(f"Level up. You are now level {shadow.level}.")

    else:

        speak("There is no active quest.")


def check_status():

    speak(shadow.status())


INTENT_ACTIONS = {

    "time_intent": tell_time,
    "shutdown_intent": shutdown_system,
    "new_quest_intent": assign_quest,
    "complete_quest_intent": complete_quest,
    "status_intent": check_status,

}


# ==============================
# MAIN EXECUTE
# ==============================

def execute(command):

    if not command:
        return

    if is_speaking:
        return

    command = command.lower().strip()

    update_last_command(command)

    command = command.replace("the quest", "quest")

    print("DEBUG EXECUTE:", command)

    # -------------------------
    # USER PROFILE
    # -------------------------

    if command.startswith("my name is"):

        name = command.replace("my name is", "").strip()

        if name:

            set_name(name)
            update_user(name)

            speak(f"I will remember that your name is {name}.")

        return


    if "what is my name" in command:

        name = get_name()

        if name:
            speak(f"Your name is {name}")
        else:
            speak("I do not know your name yet.")

        return


    if command.startswith("my goal is"):

        goal = command.replace("my goal is", "").strip()

        if goal:

            add_goal(goal)
            speak("Goal recorded.")

        return


    if (
        "what is my goal" in command
        or "what are my goals" in command
        or "show my goal" in command
        or "show my goals" in command
    ):

        goals = get_goals()

        if goals:

            if len(goals) == 1:
                speak(f"Your goal is {goals[0]}")

            else:
                speak("Your goals are " + ", ".join(goals))

        else:
            speak("You have not set any goals yet.")

        return


    # -------------------------
    # BROWSER COMMANDS
    # -------------------------

    if command.startswith("open "):

        site = command.replace("open ", "")

        speak(f"Opening {site}")
        open_generic_website(site)

        return


    if command.startswith("switch to ") or command.startswith("go to "):

        site = command.replace("switch to ", "").replace("go to ", "")

        success = switch_to_tab(site)

        if success:
            speak(f"Switching to {site}")
        else:
            speak(f"{site} is not currently open.")

        return


    if "list open tabs" in command or "what tabs are open" in command:

        tabs = list_open_tabs()

        if tabs:

            speak("Currently open tabs are " + ", ".join(tabs))

        else:
            speak("There are no open browser tabs.")

        return


    if any(p in command for p in ["close all tabs", "close all", "close everything", "close browser"]):

        speak("Closing all browser tabs.")

        close_all_tabs()

        return


    if command.startswith("close "):

        site = command.replace("close ", "")

        success = close_specific_tab(site)

        if success:
            speak(f"Closing {site}")
        else:
            speak(f"{site} is not currently open.")

        return


    # -------------------------
    # QUEST REQUESTS (category + random)
    # -------------------------
    if "quest" in command and command.startswith("give me"):
        cmd = command

        # CATEGORY QUESTS
        if "fitness" in cmd:
            assign_quest("fitness")
            return
        if "self improvement" in cmd or ("self" in cmd and "improvement" in cmd):
            assign_quest("self_improvement")
            return
        if "btech" in cmd or "b tech" in cmd or "b-tech" in cmd or ("study" in cmd and "quest" in cmd):
            assign_quest("btech")
            return

        # RANDOM QUEST (e.g., "give me a quest")
        if cmd in {"give me a quest", "give me quest"} or cmd.startswith("give me a quest"):
            assign_quest(None)
            return

    # -------------------------
    # MACHINE LEARNING INTENTS
    # -------------------------

    intent_name, confidence = predict_intent(command)

    if not intent_name or confidence < 0.40:

        speak("Sorry?")
        return


    print(f"[ML INTENT] {intent_name} (Confidence: {confidence:.2f})")


    if intent_name in INTENT_ACTIONS:

        INTENT_ACTIONS[intent_name]()


    elif intent_name == "list_tabs_intent":

        tabs = list_open_tabs()

        if tabs:
            speak("Open tabs are " + ", ".join(tabs))
        else:
            speak("No tabs are open.")


    elif intent_name == "close_all_tabs_intent":

        speak("Closing all tabs.")
        close_all_tabs()


    elif intent_name == "close_tab_intent":

        speak("Which tab should I close?")
        site = listen()

        if site:
            close_specific_tab(site)


    elif intent_name == "switch_tab_intent":

        speak("Which tab should I switch to?")
        site = listen()

        if site:
            switch_to_tab(site)


    # -------------------------
    # CONTROLLED LEARNING
    # -------------------------

    if confidence > 0.65 and len(command.split()) > 2:

        add_training_example(intent_name, command)
