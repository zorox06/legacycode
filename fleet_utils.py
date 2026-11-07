# fleet_utils.py
# Modern utility helpers for fleet reporting and unit conversions.

import statistics
from typing import Sequence

# 1 kilometer = ~0.621371 miles (1 mile = 1.609344 km)
MILES_PER_KM: float = 0.621371192


def km_to_miles(km: float) -> float:
    """Convert kilometers to miles."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format floating point number to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a percentage value."""
    return f"{value:.0f}%"


def mean(values: Sequence[float]) -> float:
    """Calculate the arithmetic mean of a sequence of numbers."""
    if not values:
        return 0.0
    return float(statistics.mean(values))
