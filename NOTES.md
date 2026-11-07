# What I checked, and what the agent got wrong

## What the agent got wrong
When initially inspecting the legacy codebase, the agent made several subtle misjudgments that had to be caught and corrected:

1. **Inverted Unit Conversion in `fleet_utils.py`**: The agent initially assumed the helper was merely suffering from floating-point inaccuracy. However, inspecting the constant revealed `MILES_PER_KM = 1.609`. Because 1 mile is approximately 1.60934 kilometers, converting kilometers to miles requires multiplying by ~0.621371 (or dividing by 1.60934). The legacy code multiplied kilometers by 1.609, reporting 160.9 miles for 100 km instead of 62.1 miles.
2. **Treating Missing Readings as Zero**: In `km_wachter.py`, the legacy fallback `car.get("last_service_km", 0)` assumed that missing odometer history could be treated as 0. For a car with 92,000 km, this implied 92,000 km since last service (over 600% wear), causing false service alerts. The agent needed to be directed to explicitly verify the presence of `last_service_km` and return `False` when readings are absent, rather than assuming unserviced status.
3. **Integer Division in Averages and Percentages**: Both `wear_percent` in `km_wachter.py` and `fleet_summary` in `fleet_report.py` used floor division (`//`). This floored wear at 14,900 / 15,000 km to 0% and suppressed fleet average wear to 0%. Both needed conversion to true float division.
4. **Data Assumptions in `analyze.py`**: The agent initially leaned toward standard intuition—assuming vehicle age and total odometer reading would be primary breakdown predictors. Directly auditing the dataset proved that neither lifetime mileage nor age has any predictive power for this fleet.

## What I checked before I accepted its work
Before signing off on the refactored repository, I ran comprehensive verification checks:

1. **Rule Invariance**: Verified that `SERVICE_INTERVAL_KM = 15000` and `WARN_AT_PERCENT = 80` remained untouched in both `km_wachter.py` and `settings.cfg`. I ensured configuration loader parsing matched settings values exactly without drift.
2. **Wear Threshold Boundaries**: Checked edge cases around the 80% warning threshold: a vehicle at 11,999 km (79.99%) is not flagged, 12,000 km (80.0%) is flagged, and 14,900 km (99.33%) is flagged.
3. **Missing Value Resilience**: Confirmed that missing `last_service_km` attributes (such as in `VOS-7788`) do not raise `KeyError` or crash `car_wear()`, `fleet_summary()`, or `print_report()`.
4. **Test Suite Execution**: Added the missing test for unrecorded service readings in `test_fleet_report.py` and ran the full suite via `pytest`. All 4 tests across `test_fleet_report.py` and `test_km_wachter.py` pass cleanly.
5. **Acceptance Verification**: Ran `python verify.py` to confirm that all 11 automated acceptance checks report green `PASS`.

## What the data actually said
A rigorous analysis of `fleet_history.csv` across all 120 cars (26 breakdowns, 94 non-breakdowns) yielded counterintuitive but unequivocal findings:

- **Lifetime Mileage (`odometer_km`)**: Showed virtually zero correlation with breakdowns (`r = +0.0022`). The mean lifetime mileage for cars that broke down was 53,448 km compared to 53,302 km for cars that did not break down (+0.3% difference). High-mileage cars that are maintained do not fail more frequently.
- **Vehicle Age (`age_years`)**: Also showed no correlation (`r = -0.0012`). Cars that broke down averaged 5.88 years, while cars that did not averaged 5.89 years.
- **True Predictors of Breakdown**:
  - `km_since_service` (`r = +0.4042`): Vehicles that broke down had accumulated an average of 11,678 km since their last service versus 7,261 km for those that did not (+60.8% increase).
  - `avg_daily_km` (`r = +0.2524`): High daily utilization significantly accelerates breakdown risk (159.7 km/day vs 131.4 km/day, +21.5%).
  - `load_factor` (`r = +0.2153`): Severe operating duty cycles and engine load correlate directly with mechanical failure (0.60 vs 0.51, +18.8%).

These empirical findings formed the basis of our composite 0-100 risk score in `analyze.py`, which weights maintenance recency (50%), daily mileage intensity (25%), and load factor (25%), enabling the fleet team to service high-risk vehicles proactively before failure.
