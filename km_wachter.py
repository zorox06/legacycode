# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Modernized and refactored from the 2013 legacy codebase.

SERVICE_INTERVAL_KM: int = 15000
WARN_AT_PERCENT: int = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Calculate the percentage of service interval consumed."""
    if interval <= 0:
        return 0.0
    return (km_since_service / interval) * 100.0


def needs_service(car: dict) -> bool:
    """Determine whether a car is due for service.

    A car is flagged if its wear percentage reaches or exceeds WARN_AT_PERCENT.
    Cars with no recorded last_service_km reading cannot have wear calculated
    and are not flagged.
    """
    if "last_service_km" not in car or car.get("last_service_km") is None:
        return False
    km_since = car["odometer"] - car["last_service_km"]
    pct = wear_percent(km_since, SERVICE_INTERVAL_KM)
    return pct >= WARN_AT_PERCENT


def check_fleet(fleet: list[dict]) -> list[str]:
    """Inspect the fleet and return a list of car IDs that require servicing."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
