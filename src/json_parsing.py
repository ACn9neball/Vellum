import json
from pathlib import Path
from platformdirs import user_config_dir

APP_NAME = "vellum"
APP_AUTHOR = "Personal"

config_dir = Path(user_config_dir(APP_NAME, APP_AUTHOR))
settings_file = config_dir / "settings.json"


def load_settings():
    default_settings = {
        "theme": "Light",
        "folder_path": "/home/",
        "background_color": "Automatic",
        "reading_mode": "LTR",
        "page_layout": "Single Page",
        "fullscreen": False,
        "animation": False,
        "scale_type": "Fit Screen",
        "swapped_page": False,
    }
    if not settings_file.exists():
        save_settings(default_settings)
        return default_settings

    with open(settings_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(data):
    config_dir.mkdir(parents=True, exist_ok=True)

    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
