# memory_manager.py

import json
import os

MEMORY_FILE = "memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {
            "name": None,
            "goals": [],
            "preferences": {"tone": "dark"},
            "last_quest": None
        }

    with open(MEMORY_FILE, "r") as file:
        return json.load(file)


def save_memory(data):
    with open(MEMORY_FILE, "w") as file:
        json.dump(data, file, indent=4)


def get_memory(key):
    memory = load_memory()
    return memory.get(key)


def update_memory(key, value):
    memory = load_memory()
    memory[key] = value
    save_memory(memory)


def add_goal(goal):
    memory = load_memory()
    if goal not in memory["goals"]:
        memory["goals"].append(goal)
        save_memory(memory)


def get_goals():
    memory = load_memory()
    return memory.get("goals", [])


def set_name(name):
    memory = load_memory()
    memory["name"] = name
    save_memory(memory)


def get_name():
    memory = load_memory()
    return memory.get("name")