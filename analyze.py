# analyze.py
# SUMMARY:
# Breakdowns are driven by km_since_service (r=+0.40), avg_daily_km (r=+0.25), and load_factor (r=+0.22).
# Lifetime odometer (r=+0.002) and vehicle age (r=-0.001) do not predict breakdowns; recent duty cycle and wear pace matter most.

"""KM-Waechter Predictive Risk Analysis.

Evaluates historical breakdown patterns across 120 fleet vehicles to identify true
breakdown predictors and calculate risk scores before cars reach the 80% wear threshold.
"""

from typing import Tuple
import pandas as pd


def load_and_analyze_data(filepath: str = "fleet_history.csv") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load fleet history and compute correlation metrics with breakdown events."""
    df = pd.read_csv(filepath)

    candidate_features = [
        "odometer_km",
        "km_since_service",
        "avg_daily_km",
        "load_factor",
        "age_years",
    ]

    # Calculate Pearson correlations against the breakdown target
    correlations = df[candidate_features].apply(lambda col: col.corr(df["broke_down"]))

    print("==================================================")
    print("FLEET BREAKDOWN FEATURE ANALYSIS")
    print("==================================================")
    print("Feature correlation with breakdown (broke_down = 1):")
    for feat, r in correlations.items():
        print(f"  {feat:20s}: r = {r:+.4f}")
    print("\nMean feature values by breakdown outcome:")
    grouped_means = df.groupby("broke_down")[candidate_features].mean().T
    grouped_means.columns = ["No Breakdown (0)", "Broke Down (1)"]
    print(grouped_means)
    print("==================================================\n")

    return df, correlations


def calculate_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate a normalized 0-100 risk score based on proven predictive indicators.

    Predictive factors:
      - km_since_service (50% weight): wear accumulation since last maintenance
      - avg_daily_km (25% weight): daily driving intensity and stress pace
      - load_factor (25% weight): severe operating conditions
    Non-predictive factors (odometer_km, age_years) are intentionally excluded.
    """
    scored_df = df.copy()

    predictive_cols = ["km_since_service", "avg_daily_km", "load_factor"]
    normalized_cols = {}

    for col in predictive_cols:
        col_min = scored_df[col].min()
        col_max = scored_df[col].max()
        if col_max > col_min:
            normalized_cols[col] = (scored_df[col] - col_min) / (col_max - col_min)
        else:
            normalized_cols[col] = 0.0

    raw_score = (
        0.50 * normalized_cols["km_since_service"]
        + 0.25 * normalized_cols["avg_daily_km"]
        + 0.25 * normalized_cols["load_factor"]
    ) * 100.0

    scored_df["risk_score"] = raw_score.round(1)
    return scored_df


def main() -> None:
    """Execute risk scoring pipeline and print ranked fleet risk."""
    df, _ = load_and_analyze_data("fleet_history.csv")
    scored_df = calculate_risk_scores(df)

    ranked_fleet = scored_df.sort_values(by="risk_score", ascending=False)

    print("TOP 15 HIGHEST RISK CARS (Prioritize for immediate proactive inspection):")
    display_cols = [
        "car_id",
        "risk_score",
        "km_since_service",
        "avg_daily_km",
        "load_factor",
        "odometer_km",
        "broke_down",
    ]
    print(ranked_fleet[display_cols].head(15).to_string(index=False))

    print("\nAverage risk score by historical breakdown status:")
    print(f"  Cars that broke down:     {scored_df[scored_df['broke_down'] == 1]['risk_score'].mean():.1f}")
    print(f"  Cars that did not break:  {scored_df[scored_df['broke_down'] == 0]['risk_score'].mean():.1f}")


if __name__ == "__main__":
    main()
