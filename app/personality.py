from pathlib import Path

import yaml


PERSONALITY_PATH = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "personality.yaml"
)


def load_personality() -> str:
    with open(PERSONALITY_PATH, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return yaml.safe_dump(config, sort_keys=False)