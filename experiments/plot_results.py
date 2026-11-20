from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import t

ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

SUMMARY_FILE = RESULTS_DIR / "statistical_summary.csv"

SCENARIOS = [
    "baseline_10x3",
    "baseline_25x3",
    "baseline_50x3",
]

SCHEDULERS = ["FIFO", "SPT", "EDD"]

EXPECTED_EXPERIMENT_COUNT = 30
CONFIDENCE_LEVEL = 0.95

METRICS = {
    "makespan": "Makespan",
    "mean_flow_time": "Mean Flow Time",
    "total_tardiness": "Total Tardiness",
    "mean_tardiness": "Mean Tardiness",
    "overall_machine_utilization": "Overall Machine Utilization (%)",
    "utilization_M1": "Machine M1 Utilization (%)",
    "utilization_M2": "Machine M2 Utilization (%)",
    "utilization_M3": "Machine M3 Utilization (%)",
}


def load_summary() -> pd.DataFrame:
    """Load and validate statistical summary results."""

    if not SUMMARY_FILE.exists():
        raise FileNotFoundError(
            f"Statistical summary not found: {SUMMARY_FILE}"
        )

    df = pd.read_csv(SUMMARY_FILE)

    required_columns = [
        "scenario_id",
        "scheduler",
        "experiment_count",
    ]

    for metric in METRICS:
        required_columns.extend(
            [
                f"{metric}_mean",
                f"{metric}_std",
            ]
        )

    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing columns in summary CSV: {sorted(missing)}"
        )

    if df[required_columns].isnull().any().any():
        raise ValueError(
            "Summary CSV contains missing values."
        )

    if df.duplicated(
        subset=["scenario_id", "scheduler"]
    ).any():
        raise ValueError(
            "Duplicate scenario/scheduler combinations found."
        )

    actual_scenarios = set(df["scenario_id"])
    expected_scenarios = set(SCENARIOS)

    if actual_scenarios != expected_scenarios:
        raise ValueError(
            "Unexpected scenario configuration. "
            f"Expected: {sorted(expected_scenarios)}, "
            f"got: {sorted(actual_scenarios)}"
        )

    actual_schedulers = set(df["scheduler"])
    expected_schedulers = set(SCHEDULERS)

    if actual_schedulers != expected_schedulers:
        raise ValueError(
            "Unexpected scheduler configuration. "
            f"Expected: {sorted(expected_schedulers)}, "
            f"got: {sorted(actual_schedulers)}"
        )

    expected_rows = len(SCENARIOS) * len(SCHEDULERS)

    if len(df) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows} summary rows, "
            f"got {len(df)}."
        )

    numeric_columns = ["experiment_count"]

    for metric in METRICS:
        numeric_columns.extend(
            [
                f"{metric}_mean",
                f"{metric}_std",
            ]
        )

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="raise",
        )

    if not np.isfinite(
        df[numeric_columns].to_numpy(dtype=float)
    ).all():
        raise ValueError(
            "Summary CSV contains non-finite numeric values."
        )

    if (
        df["experiment_count"] != EXPECTED_EXPERIMENT_COUNT
    ).any():
        raise ValueError(
            "Every scenario/scheduler combination must contain "
            f"exactly {EXPECTED_EXPERIMENT_COUNT} experiments."
        )

    for metric in METRICS:
        std_column = f"{metric}_std"

        if (df[std_column] < 0).any():
            raise ValueError(
                f"Negative standard deviation detected: {metric}"
            )

    return df


def calculate_confidence_interval(
    std: float,
    sample_size: int,
) -> float:
    """
    Calculate the half-width of a two-sided Student's t confidence
    interval for the mean.

    Assumes std is the sample standard deviation.
    """

    if sample_size < 2:
        raise ValueError(
            "Sample size must be at least 2."
        )

    if std < 0:
        raise ValueError(
            "Standard deviation cannot be negative."
        )

    alpha = 1.0 - CONFIDENCE_LEVEL
    degrees_of_freedom = sample_size - 1

    critical_value = t.ppf(
        1.0 - alpha / 2.0,
        degrees_of_freedom,
    )

    standard_error = std / np.sqrt(sample_size)

    return float(
        critical_value * standard_error
    )


def plot_metric(
    df: pd.DataFrame,
    metric: str,
    title: str,
) -> None:
    """Plot scheduler means with 95% confidence intervals."""

    fig, axes = plt.subplots(
        1,
        len(SCENARIOS),
        figsize=(15, 5.5),
        sharey=False,
    )

    try:
        for ax, scenario in zip(axes, SCENARIOS):
            scenario_df = (
                df[df["scenario_id"] == scenario]
                .set_index("scheduler")
                .reindex(SCHEDULERS)
            )

            columns = [
                f"{metric}_mean",
                f"{metric}_std",
                "experiment_count",
            ]

            if scenario_df[columns].isnull().any().any():
                raise ValueError(
                    f"Missing data for {scenario}, metric {metric}."
                )

            means = scenario_df[
                f"{metric}_mean"
            ].to_numpy(dtype=float)

            stds = scenario_df[
                f"{metric}_std"
            ].to_numpy(dtype=float)

            sample_sizes = scenario_df[
                "experiment_count"
            ].to_numpy(dtype=int)

            ci_half_widths = np.array(
                [
                    calculate_confidence_interval(std, n)
                    for std, n in zip(stds, sample_sizes)
                ]
            )

            x_positions = np.arange(len(SCHEDULERS))

            ax.errorbar(
                x_positions,
                means,
                yerr=ci_half_widths,
                fmt="o",
                linestyle="none",
                capsize=5,
                elinewidth=1.5,
                markersize=8,
            )

            ax.set_xticks(x_positions)
            ax.set_xticklabels(SCHEDULERS)

            ax.set_title(
                scenario.replace("_", " ").upper()
            )

            ax.set_xlabel("Scheduling Algorithm")
            ax.set_ylabel(title)

            ax.grid(
                True,
                axis="y",
                alpha=0.3,
            )

        fig.suptitle(
            f"{title}: Mean and "
            f"{CONFIDENCE_LEVEL:.0%} Confidence Interval",
            fontsize=14,
        )

        fig.tight_layout()

        png_file = FIGURES_DIR / f"{metric}_comparison.png"
        pdf_file = FIGURES_DIR / f"{metric}_comparison.pdf"

        fig.savefig(
            png_file,
            dpi=300,
            bbox_inches="tight",
        )

        fig.savefig(
            pdf_file,
            format="pdf",
            bbox_inches="tight",
        )

        print(f"Saved: {png_file}")
        print(f"Saved: {pdf_file}")

    finally:
        plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = load_summary()

    print("=" * 65)
    print("BASELINE PERFORMANCE VISUALIZATION")
    print("=" * 65)

    print(
        "Experiments per scheduler/scenario:",
        sorted(df["experiment_count"].unique()),
    )

    print(f"Scenarios: {df['scenario_id'].nunique()}")
    print(f"Schedulers: {df['scheduler'].nunique()}")
    print(f"Metrics: {len(METRICS)}")

    for metric, title in METRICS.items():
        print(f"\nGenerating figures: {title}")
        plot_metric(df, metric, title)

    print("\n" + "=" * 65)
    print(f"Total metrics visualized: {len(METRICS)}")
    print(f"Total figures generated: {len(METRICS) * 2}")
    print(f"Figures saved in: {FIGURES_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    main()
