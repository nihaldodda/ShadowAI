# shadow_state.py

from shadow_gui import update_xp, update_level, update_rank


class ShadowState:

    def __init__(self):

        self.level = 1
        self.xp = 0

        self.rank = "E"
        self.rank_name = "Initiate of Shadows"

        self.just_leveled_up = False
        self.rank_promoted = False

        self.previous_rank = "E"
        self.previous_rank_name = "Initiate of Shadows"

        # Initialize GUI
        update_level(self.level)
        update_xp(self.xp)
        update_rank(f"{self.rank} - {self.rank_name}")

    # ==============================

    def gain_xp(self, amount):

        self.just_leveled_up = False
        self.rank_promoted = False

        self.xp += amount

        update_xp(self.xp)

        self.check_level_up()

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