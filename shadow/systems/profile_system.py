"""User profile: name and goals (persisted via core memory)."""
from shadow.core.memory_manager import add_goal, get_goals, get_name, set_name

__all__ = ["add_goal", "get_goals", "get_name", "set_name"]
