from pathlib import Path
import yaml

CONFIG_FILE = Path("config/settings.yaml")


def load_config():
    if not CONFIG_FILE.exists():
        return {}

    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)
