"""Paths and application configuration (no runtime side effects)."""
import os

# shadow/utils/config.py -> shadow package root
SHADOW_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SHADOW_ROOT, "data")
ASSETS_DIR = os.path.join(SHADOW_ROOT, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
