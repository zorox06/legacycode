# config_loader.py
# Reads configuration settings from settings.cfg.

SETTINGS_FILE: str = "settings.cfg"

KNOWN_KEYS: set[str] = {
    "service_interval_km",
    "warn_at_percent",
    "report_title",
    "history_file",
    "log_file",
    "mileage_unit",
}


def load_settings(path: str | None = None) -> dict[str, str]:
    """Load settings from the specified configuration file."""
    if path is None:
        path = SETTINGS_FILE

    settings: dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key in KNOWN_KEYS:
                settings[key] = value

    return settings


def get_int(settings: dict[str, str], key: str, fallback: int) -> int:
    """Retrieve an integer setting with fallback."""
    if key in settings:
        try:
            return int(settings[key])
        except ValueError:
            return fallback
    return fallback


def get_setting(settings: dict[str, str], key: str, fallback: str = "") -> str:
    """Retrieve a string setting with fallback."""
    return settings.get(key, fallback)
