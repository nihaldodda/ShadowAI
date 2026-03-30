# shadow_state.py

from shadow.core.memory_manager import increment_completed_quests, load_memory, save_shadow_progress
from shadow.ui.shadow_gui import update_level, update_rank, update_xp


class ShadowState:

    def __init__(self):

        memory = load_memory()

        self.level = int(memory.get("level", 1))
        self.xp = int(memory.get("xp", 0))

        self.rank = "E"
        self.rank_name = "Initiate of Shadows"

        self.just_leveled_up = False
        self.rank_promoted = False

        self.previous_rank = "E"
        self.previous_rank_name = "Initiate of Shadows"

        self.update_rank()

        self.just_leveled_up = False
        self.rank_promoted = False

        # Initialize GUI
        update_level(self.level)
        update_xp(self.xp)
        update_rank(f"{self.rank} - {self.rank_name}")

        save_shadow_progress(self.level, self.xp, self.rank, self.rank_name)

    # ==============================

    def gain_xp(self, amount):

        self.just_leveled_up = False
        self.rank_promoted = False

        self.xp += amount

        update_xp(self.xp)

        self.check_level_up()

        save_shadow_progress(self.level, self.xp, self.rank, self.rank_name)

        if amount > 0:
            increment_completed_quests()

    # ==============================

    def check_level_up(self):

        xp_needed = self.level * 100

        if self.xp >= xp_needed:

            self.level += 1
            self.xp = 0

            self.just_leveled_up = True

            update_level(self.level)
            update_xp(self.xp)

            self.update_rank()

    # ==============================

    def update_rank(self):

        self.previous_rank = self.rank
        self.previous_rank_name = self.rank_name

        if self.level >= 11:

            self.rank = "S"
            self.rank_name = "Shadow Monarch"

        elif self.level >= 9:

            self.rank = "A"
            self.rank_name = "Abyss Commander"

        elif self.level >= 7:

            self.rank = "B"
            self.rank_name = "Shadow Lord"

        elif self.level >= 5:

            self.rank = "C"
            self.rank_name = "Shadow Hunter"

        elif self.level >= 3:

            self.rank = "D"
            self.rank_name = "Shadow Walker"

        else:

            self.rank = "E"
            self.rank_name = "Initiate of Shadows"

        update_rank(f"{self.rank} - {self.rank_name}")

        if self.rank != self.previous_rank:
            self.rank_promoted = True

    # ==============================

    def status(self):

        return (
            f"You are Level {self.level}. "
            f"Rank: {self.rank} - {self.rank_name}. "
            f"Current experience: {self.xp}."
        )
