from pathlib import Path

import matplotlib.pyplot as plt
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

METRICS = {
    "makespan": "Makespan",
    "mean_flow_time": "Mean Flow Time",
    "total_tardiness": "Total Tardiness",
}


def load_summary() -> pd.DataFrame:
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
            [f"{metric}_mean", f"{metric}_std"]
        )

    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing columns in summary CSV: {sorted(missing)}"
        )

    if df[required_columns].isnull().any().any():
        raise ValueError("Summary CSV contains missing values.")

    if df.duplicated(["scenario_id", "scheduler"]).any():
        raise ValueError(
            "Duplicate scenario/scheduler combinations found."
        )

    if not set(SCENARIOS).issubset(set(df["scenario_id"])):
        raise ValueError("One or more expected scenarios are missing.")

    if not set(SCHEDULERS).issubset(set(df["scheduler"])):
        raise ValueError("One or more expected schedulers are missing.")

    if (df["experiment_count"] < 2).any():
        raise ValueError("At least two experiments are required.")

    for metric in METRICS:
        if (df[f"{metric}_std"] < 0).any():
            raise ValueError(f"Negative standard deviation: {metric}")

    return df


def calculate_confidence_interval(
    mean: float,
    std: float,
    sample_size: int,
) -> float:
    """
    Calculate the half-width of a two-sided 95% Student's t CI.
    Assumes std is the sample standard deviation.
    """
    degrees_of_freedom = sample_size - 1

    critical_value = t.ppf(
        0.975,
        degrees_of_freedom,
    )

    standard_error = std / (sample_size ** 0.5)

    return critical_value * standard_error


def plot_metric(
    df: pd.DataFrame,
    metric: str,
    title: str,
) -> None:
    fig, axes = plt.subplots(
        1,
        3,
        figsize=(15, 5.5),
    )

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
                f"Missing data for {scenario}, metric {metric}"
            )

        means = scenario_df[f"{metric}_mean"].to_numpy()
        stds = scenario_df[f"{metric}_std"].to_numpy()

        sample_sizes = (
            scenario_df["experiment_count"]
            .astype(int)
            .to_numpy()
        )

        ci_half_widths = [
            calculate_confidence_interval(mean, std, n)
            for mean, std, n in zip(
                means,
                stds,
                sample_sizes,
            )
        ]

        x_positions = range(len(SCHEDULERS))

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

        ax.set_xticks(list(x_positions))
        ax.set_xticklabels(SCHEDULERS)

        ax.set_title(scenario.replace("_", " ").upper())
        ax.set_xlabel("Scheduling Algorithm")
        ax.set_ylabel(title)

        ax.grid(
            True,
            axis="y",
            alpha=0.3,
        )

    fig.suptitle(
        f"{title}: Mean and 95% Confidence Interval",
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

    plt.close(fig)

    print(f"Saved: {png_file}")
    print(f"Saved: {pdf_file}")


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = load_summary()

    print("=" * 60)
    print("BASELINE PERFORMANCE VISUALIZATION")
    print("=" * 60)

    print(
        "Experiments per scheduler/scenario:",
        sorted(df["experiment_count"].unique()),
    )

    print(f"Scenarios: {df['scenario_id'].nunique()}")
    print(f"Schedulers: {df['scheduler'].nunique()}")

    for metric, title in METRICS.items():
        plot_metric(df, metric, title)

    print("=" * 60)
    print(f"All figures saved in: {FIGURES_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
