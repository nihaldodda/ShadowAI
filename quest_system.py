import random


class Quest:
    def __init__(self, title, description, xp_reward):
        self.title = title
        self.description = description
        self.xp_reward = xp_reward


class QuestSystem:
    def __init__(self):
        self.active_quest = None

        self.quest_pool = [
            Quest(
                "Discipline Trial",
                "Work focused for 25 minutes without distraction.",
                50
            ),
            Quest(
                "Mind Sharpening",
                "Read 10 pages of a book.",
                40
            ),
            Quest(
                "Body Strengthening",
                "Do 30 pushups.",
                60
            ),
            Quest(
                "Knowledge Hunt",
                "Learn one new technical concept today.",
                70
            ),
        ]

    def assign_random_quest(self):
        self.active_quest = random.choice(self.quest_pool)
        print(f"[DEBUG QUEST] Assigned: {self.active_quest.title}")
        return self.active_quest

    def complete_quest(self):
        if self.active_quest:
            xp = self.active_quest.xp_reward
            print(f"[DEBUG QUEST] Completed: {self.active_quest.title}")
            self.active_quest = None
            return xp
        else:
            print("[DEBUG QUEST] No active quest.")
            return 0