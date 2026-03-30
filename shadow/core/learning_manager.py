import json
import os

from shadow.utils.config import DATA_DIR
from shadow.utils.helpers import ensure_data_dir

LEARNED_FILE = os.path.join(DATA_DIR, "learned_data.json")


def load_learned_data():
    if not os.path.exists(LEARNED_FILE):
        return {}

    with open(LEARNED_FILE, "r") as f:
        return json.load(f)


def save_learned_data(data):
    ensure_data_dir()
    with open(LEARNED_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_training_example(intent_name, sentence):
    data = load_learned_data()

    if intent_name not in data:
        data[intent_name] = []

    if sentence not in data[intent_name]:
        data[intent_name].append(sentence)
        save_learned_data(data)
        print(f"[AUTO-LEARN] Learned new phrase for {intent_name}")
