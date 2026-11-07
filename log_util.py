# log_util.py
# Logging utility for KM-Waechter.

import time

LOG_LINES: list[str] = []
DEBUG: bool = False


def log(message: str) -> None:
    """Format, print, and buffer a timestamped log message."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def debug(message: str) -> None:
    """Log a debug message if debug logging is enabled."""
    if DEBUG:
        log(f"DEBUG: {message}")


def flush_log(path: str) -> None:
    """Flush buffered log lines to a file and clear the memory buffer."""
    with open(path, "a", encoding="utf-8") as f:
        for line in LOG_LINES:
            f.write(f"{line}\n")
    LOG_LINES.clear()
