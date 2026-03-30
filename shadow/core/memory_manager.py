# memory_manager.py

import json
import os

from shadow.utils.config import DATA_DIR
from shadow.utils.helpers import ensure_data_dir

MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")

_PROGRESS_DEFAULTS = {
    "xp": 0,
    "level": 1,
    "rank": "Beginner",
    "completed_quests": 0,
}


def _merge_progress_defaults(data):
    for key, default in _PROGRESS_DEFAULTS.items():
        if key not in data:
            data[key] = default
    if "rank_name" not in data:
        data["rank_name"] = None
    return data


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return _merge_progress_defaults(
            {
                "name": None,
                "goals": [],
                "preferences": {"tone": "dark"},
                "last_quest": None,
            }
        )

    with open(MEMORY_FILE, "r") as file:
        data = json.load(file)
    return _merge_progress_defaults(data)


def save_memory(data):
    ensure_data_dir()
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


def save_shadow_progress(level, xp, rank_code, rank_name):
    """Persist Shadow assistant level, XP, and rank (mirrors shadow_state)."""
    memory = load_memory()
    memory["level"] = int(level)
    memory["xp"] = int(xp)
    memory["rank"] = str(rank_code)
    memory["rank_name"] = str(rank_name)
    save_memory(memory)


def increment_completed_quests():
    memory = load_memory()
    memory["completed_quests"] = int(memory.get("completed_quests", 0)) + 1
    save_memory(memory)
