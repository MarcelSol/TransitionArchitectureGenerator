from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_FILE = PROJECT_ROOT / "config" / "settings.yaml"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}

    with CONFIG_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return yaml.safe_load(file) or {}
