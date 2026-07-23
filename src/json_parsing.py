import json
from pathlib import Path
from platformdirs import user_config_dir

APP_NAME = "vellum"
APP_AUTHOR = "Personal"

config_dir = Path(user_config_dir(APP_NAME, APP_AUTHOR))
settings_file = config_dir / "settings.json"
recents_file = config_dir / "recents.json"


def load_settings():
    default_settings = {
        "theme": "Default",
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


def reset_settings():
    settings_file.unlink(missing_ok=True)
    load_settings()


def load_recents():
    default_recents = {"recent_files": [], "recent_file_pages": []}
    if not recents_file.exists():
        save_recents(default_recents)
        return default_recents

    with open(recents_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_recents(data):
    config_dir.mkdir(parents=True, exist_ok=True)

    with open(recents_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def reset_recents():
    recents_file.unlink(missing_ok=True)
    load_recents()


def save_recent(data, path):
    recents = data["recent_files"]
    found = False
    index = 0
    for recent in recents:
        if recent == path:
            found = True
            break
        index += 1

    if found:
        recents.pop(index)
        recents.append(path)
    else:
        if len(recents) < 55:
            recents.append(path)
        else:
            recents.pop(0)
            recents.append(path)

    save_recents(data)
    return load_recents()
