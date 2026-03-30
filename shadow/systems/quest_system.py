from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass

from shadow.core.memory_manager import load_memory, update_memory
from shadow.utils.config import DATA_DIR


@dataclass
class QuestTask:
    task: str
    xp: int


class Quest:
    """Quest object consumed by existing UI + XP logic."""

    def __init__(self, title: str, description: str, xp_reward: int, category: str | None = None):
        self.title = title
        self.description = description
        self.xp_reward = int(xp_reward)
        self.category = category


class QuestSystem:
    """Category-aware quest generation with persistence + duplicate prevention."""

    _CATEGORIES = ("fitness", "btech", "self_improvement")

    def __init__(self):
        self.active_quest: Quest | None = None
        self._quest_catalog = self._load_catalog()
        self._last_generated_key: str | None = None

        self._restore_active_quest_from_memory()

        # Preserve legacy attribute for any debug usage.
        self.quest_pool: list[Quest] = self._flatten_quest_pool()

    def _data_file(self) -> str:
        return os.path.join(DATA_DIR, "quest_data.json")

    def _load_catalog(self) -> dict[str, list[QuestTask]]:
        # Fallback to the previous static pool if data is missing/unexpected.
        fallback = {
            "fitness": [
                QuestTask("Do 30 pushups", 60),
                QuestTask("Stretch for 5 minutes", 8),
            ],
            "btech": [
                QuestTask("Revise lecture notes", 15),
                QuestTask("Solve 2 programming problems", 25),
            ],
            "self_improvement": [
                QuestTask("Read 10 pages of a book", 15),
                QuestTask("Write a short journal entry", 15),
            ],
        }

        try:
            with open(self._data_file(), "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return fallback

        # Support both shapes:
        # - { "fitness": [...], "btech": [...], ... }
        # - { "quests": { "fitness": [...], ... } }
        if isinstance(data, dict) and "quests" in data and isinstance(data["quests"], dict):
            data = data["quests"]

        if not isinstance(data, dict):
            return fallback

        catalog: dict[str, list[QuestTask]] = {}
        for key in self._CATEGORIES:
            raw_list = data.get(key) or []
            tasks: list[QuestTask] = []
            for item in raw_list:
                if not isinstance(item, dict):
                    continue
                task = str(item.get("task", "")).strip()
                xp_val = item.get("xp", 0)
                try:
                    xp = int(xp_val)
                except Exception:
                    continue
                if task and xp >= 0:
                    tasks.append(QuestTask(task=task, xp=xp))
            if tasks:
                catalog[key] = tasks

        # Ensure all categories exist (fallback where empty).
        for key in self._CATEGORIES:
            if key not in catalog:
                catalog[key] = fallback.get(key, [])

        return catalog

    def _flatten_quest_pool(self) -> list[Quest]:
        out: list[Quest] = []
        for cat, tasks in self._quest_catalog.items():
            for t in tasks:
                out.append(Quest(title=t.task, description="", xp_reward=t.xp, category=cat))
        return out

    def _quest_key(self, category: str, task: str) -> str:
        return f"{category}:{task}"

    def _restore_active_quest_from_memory(self) -> None:
        mem = load_memory()
        last = mem.get("last_quest")
        if not isinstance(last, dict):
            return

        category = last.get("category")
        task = last.get("task")
        xp = last.get("xp")
        active_flag = bool(last.get("active"))

        if not category or not task:
            return

        try:
            xp_int = int(xp)
        except Exception:
            return

        self._last_generated_key = self._quest_key(str(category), str(task))

        if active_flag:
            self.active_quest = Quest(
                title=str(task),
                description="",
                xp_reward=xp_int,
                category=str(category),
            )

    def assign_random_quest(self) -> Quest:
        category = random.choice(list(self._quest_catalog.keys()))
        return self.assign_category_quest(category)

    def assign_category_quest(self, category: str) -> Quest:
        category_key = (category or "").strip().lower().replace("-", "_").replace(" ", "_")
        if category_key not in self._quest_catalog:
            # Unknown category -> keep behavior predictable by falling back to random.
            return self.assign_random_quest()

        tasks = self._quest_catalog[category_key]
        if not tasks:
            return self.assign_random_quest()

        # Duplicate prevention: do not give the same quest twice in a row (if possible).
        chosen: QuestTask | None = None
        for _ in range(8):
            candidate = random.choice(tasks)
            cand_key = self._quest_key(category_key, candidate.task)
            if cand_key != self._last_generated_key:
                chosen = candidate
                break
        if chosen is None:
            chosen = random.choice(tasks)

        self.active_quest = Quest(
            title=chosen.task,
            description="",
            xp_reward=chosen.xp,
            category=category_key,
        )

        self._last_generated_key = self._quest_key(category_key, chosen.task)
        update_memory(
            "last_quest",
            {
                "category": category_key,
                "task": chosen.task,
                "xp": int(chosen.xp),
                "active": True,
            },
        )
        return self.active_quest

    # Backwards-compatible alias used by current command layer.
    def assign_quest(self, category: str | None = None) -> Quest:
        if category:
            return self.assign_category_quest(category)
        return self.assign_random_quest()

    def complete_quest(self) -> int:
        if not self.active_quest:
            print("[DEBUG QUEST] No active quest.")
            return 0

        xp = self.active_quest.xp_reward
        title = self.active_quest.title
        category = getattr(self.active_quest, "category", None) or ""

        print(f"[DEBUG QUEST] Completed: {title}")

        # Clear active quest but keep last quest info for persistence + duplicate prevention.
        self.active_quest = None
        update_memory(
            "last_quest",
            {
                "category": category,
                "task": title,
                "xp": int(xp),
                "active": False,
            },
        )
        return xp
