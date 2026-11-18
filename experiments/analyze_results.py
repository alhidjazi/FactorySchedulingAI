from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

INPUT_PATTERN = "baseline_*.csv"
OUTPUT_FILE = RESULTS_DIR / "statistical_summary.csv"

GROUP_COLUMNS = ["scenario_id", "scheduler"]

METRICS = [
    "makespan",
    "mean_flow_time",
    "total_tardiness",
    "mean_tardiness",
    "overall_machine_utilization",
    "utilization_M1",
    "utilization_M2",
    "utilization_M3",
]


def load_results() -> pd.DataFrame:
    """Load and combine all baseline benchmark CSV files."""

    files = sorted(RESULTS_DIR.glob(INPUT_PATTERN))

    if not files:
        raise FileNotFoundError(
            f"No benchmark CSV files found in {RESULTS_DIR}"
        )

    dataframes = []

    for file in files:
        print(f"Loading: {file.name}")
        df = pd.read_csv(file)
        dataframes.append(df)

    results = pd.concat(dataframes, ignore_index=True)

    required_columns = GROUP_COLUMNS + ["seed"] + METRICS

    missing_columns = [
        column
        for column in required_columns
        if column not in results.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    for metric in METRICS:
        results[metric] = pd.to_numeric(
            results[metric],
            errors="raise",
        )

    if results[required_columns].isnull().any().any():
        raise ValueError("Benchmark data contains missing values.")

    if results.duplicated(
        subset=["scenario_id", "seed", "scheduler"]
    ).any():
        raise ValueError("Duplicate experiment records detected.")

    return results


def calculate_statistics(results: pd.DataFrame) -> pd.DataFrame:
    """Calculate mean and sample standard deviation."""

    aggregations = {
        "experiment_count": ("seed", "count"),
        "seed_count": ("seed", "nunique"),
    }

    for metric in METRICS:
        aggregations[f"{metric}_mean"] = (metric, "mean")
        aggregations[f"{metric}_std"] = (
            metric,
            lambda values: values.std(ddof=1),
        )

    summary = (
        results
        .groupby(GROUP_COLUMNS)
        .agg(**aggregations)
        .reset_index()
    )

    return summary.sort_values(
        ["scenario_id", "scheduler"]
    )


def main() -> None:
    print("=" * 60)
    print("BASELINE STATISTICAL ANALYSIS")
    print("=" * 60)

    results = load_results()

    print(f"\nTotal experiments: {len(results)}")
    print(f"Scenarios: {results['scenario_id'].nunique()}")
    print(f"Schedulers: {results['scheduler'].nunique()}")
    print(f"Unique seeds: {results['seed'].nunique()}")

    summary = calculate_statistics(results)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    summary.to_csv(OUTPUT_FILE, index=False)

    print("\nSTATISTICAL SUMMARY")
    print("=" * 60)

    display_columns = [
        "scenario_id",
        "scheduler",
        "experiment_count",
        "makespan_mean",
        "makespan_std",
        "mean_flow_time_mean",
        "mean_flow_time_std",
        "total_tardiness_mean",
        "total_tardiness_std",
    ]

    print(
        summary[display_columns].to_string(
            index=False,
            float_format=lambda value: f"{value:.4f}",
        )
    )

    print("\n" + "=" * 60)
    print(f"Analysis saved to: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()