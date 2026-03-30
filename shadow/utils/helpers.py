"""Small shared helpers (paths, safe I/O helpers)."""
import os

from shadow.utils.config import DATA_DIR


def ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
