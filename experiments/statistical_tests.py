from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, rankdata, wilcoxon

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

INPUT_PATTERN = "baseline_*.csv"
OUTPUT_FILE = RESULTS_DIR / "statistical_tests.csv"
FRIEDMAN_OUTPUT_FILE = RESULTS_DIR / "friedman_tests.csv"

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

SCHEDULERS = ["FIFO", "SPT", "EDD"]

EXPECTED_SEEDS = 30
ALPHA = 0.05

BOOTSTRAP_ITERATIONS = 10_000
BOOTSTRAP_RANDOM_STATE = 20261120


def holm_correction(p_values) -> list[float]:
    """Apply Holm-Bonferroni correction."""

    values = np.asarray(p_values, dtype=float)

    if not np.isfinite(values).all():
        raise ValueError("P-values must be finite.")

    if ((values < 0) | (values > 1)).any():
        raise ValueError("P-values must be between 0 and 1.")

    count = len(values)

    if count == 0:
        return []

    order = np.argsort(values)
    sorted_values = values[order]

    adjusted_sorted = np.maximum.accumulate(
        (count - np.arange(count)) * sorted_values
    )

    adjusted_sorted = np.minimum(adjusted_sorted, 1.0)

    adjusted = np.empty(count, dtype=float)
    adjusted[order] = adjusted_sorted

    return adjusted.tolist()


def load_results() -> pd.DataFrame:
    """Load and validate all benchmark results."""

    files = sorted(RESULTS_DIR.glob(INPUT_PATTERN))

    if not files:
        raise FileNotFoundError(
            f"No benchmark CSV files found in {RESULTS_DIR}"
        )

    frames = [pd.read_csv(file) for file in files]
    results = pd.concat(frames, ignore_index=True)

    required = ["scenario_id", "seed", "scheduler"] + METRICS

    missing = [
        column for column in required
        if column not in results.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if results[required].isnull().any().any():
        raise ValueError("Missing values detected.")

    for metric in METRICS:
        results[metric] = pd.to_numeric(
            results[metric],
            errors="raise",
        )

    if not np.isfinite(
        results[METRICS].to_numpy(dtype=float)
    ).all():
        raise ValueError("Non-finite metric values detected.")

    if results.duplicated(
        subset=["scenario_id", "seed", "scheduler"]
    ).any():
        raise ValueError("Duplicate experiment records detected.")

    unknown_schedulers = (
        set(results["scheduler"].unique()) - set(SCHEDULERS)
    )

    if unknown_schedulers:
        raise ValueError(
            f"Unknown schedulers: {unknown_schedulers}"
        )

    for scenario in sorted(results["scenario_id"].unique()):
        scenario_data = results[
            results["scenario_id"] == scenario
        ]

        seed_sets = []

        for scheduler in SCHEDULERS:
            scheduler_data = scenario_data[
                scenario_data["scheduler"] == scheduler
            ]

            if len(scheduler_data) != EXPECTED_SEEDS:
                raise ValueError(
                    f"Expected {EXPECTED_SEEDS} records: "
                    f"{scenario}, {scheduler}. "
                    f"Got {len(scheduler_data)}."
                )

            seed_sets.append(set(scheduler_data["seed"]))

        if not all(seeds == seed_sets[0] for seeds in seed_sets):
            raise ValueError(
                f"Unmatched seeds between schedulers: {scenario}"
            )

    return results


def calculate_effect_size(a, b) -> float:
    """
    Calculate matched-pairs rank-biserial correlation.

    Positive: A tends to produce higher values than B.
    Negative: B tends to produce higher values than A.
    """

    differences = np.asarray(a, dtype=float) - np.asarray(
        b, dtype=float
    )

    differences = differences[differences != 0]

    if len(differences) == 0:
        return 0.0

    ranks = rankdata(np.abs(differences))

    positive_rank_sum = ranks[differences > 0].sum()
    negative_rank_sum = ranks[differences < 0].sum()

    total_rank_sum = positive_rank_sum + negative_rank_sum

    if total_rank_sum == 0:
        return 0.0

    return float(
        (positive_rank_sum - negative_rank_sum)
        / total_rank_sum
    )


def bootstrap_mean_ci(
    differences,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """
    Calculate a 95% percentile bootstrap CI
    for the mean paired difference.
    """

    differences = np.asarray(differences, dtype=float)

    if len(differences) == 0:
        raise ValueError("Cannot bootstrap an empty sample.")

    if np.all(differences == differences[0]):
        value = float(differences[0])
        return value, value

    samples = rng.choice(
        differences,
        size=(BOOTSTRAP_ITERATIONS, len(differences)),
        replace=True,
    )

    bootstrap_means = samples.mean(axis=1)

    lower, upper = np.quantile(
        bootstrap_means,
        [0.025, 0.975],
    )

    return float(lower), float(upper)


def run_friedman_tests(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """Run Friedman omnibus tests and global Holm correction."""

    records = []

    for scenario in sorted(results["scenario_id"].unique()):
        scenario_data = results[
            results["scenario_id"] == scenario
        ]

        for metric in METRICS:
            scheduler_data = []

            for scheduler in SCHEDULERS:
                data = (
                    scenario_data[
                        scenario_data["scheduler"] == scheduler
                    ]
                    .set_index("seed")[metric]
                    .sort_index()
                )

                scheduler_data.append(data)

            aligned = pd.concat(
                scheduler_data,
                axis=1,
                keys=SCHEDULERS,
                join="inner",
            ).sort_index()

            if len(aligned) != EXPECTED_SEEDS:
                raise ValueError(
                    f"Expected {EXPECTED_SEEDS} paired seeds: "
                    f"{scenario}, {metric}"
                )

            if not aligned.index.is_unique:
                raise ValueError(
                    f"Duplicate seeds: {scenario}, {metric}"
                )

            if aligned.nunique(axis=1).eq(1).all():
                statistic = 0.0
                p_value = 1.0
                kendall_w = 0.0
            else:
                test = friedmanchisquare(
                    *[
                        aligned[scheduler].to_numpy()
                        for scheduler in SCHEDULERS
                    ]
                )

                statistic = float(test.statistic)
                p_value = float(test.pvalue)

                kendall_w = (
                    statistic
                    / (
                        len(aligned)
                        * (len(SCHEDULERS) - 1)
                    )
                )

            records.append({
                "scenario_id": scenario,
                "metric": metric,
                "sample_size": len(aligned),
                "scheduler_count": len(SCHEDULERS),
                "friedman_statistic": statistic,
                "p_value": p_value,
                "kendall_w": kendall_w,
            })

    friedman_results = pd.DataFrame(records)

    # One Holm family containing all scenario-metric
    # Friedman omnibus tests.
    friedman_results["p_adjusted_holm"] = holm_correction(
        friedman_results["p_value"]
    )

    friedman_results["significant"] = (
        friedman_results["p_adjusted_holm"] < ALPHA
    )

    return friedman_results


def run_pairwise_tests(
    results: pd.DataFrame,
    friedman_results: pd.DataFrame,
) -> pd.DataFrame:
    """Run paired Wilcoxon post-hoc tests."""

    records = []

    friedman_lookup = friedman_results.set_index(
        ["scenario_id", "metric"]
    )

    rng = np.random.default_rng(BOOTSTRAP_RANDOM_STATE)

    for scenario in sorted(results["scenario_id"].unique()):
        scenario_data = results[
            results["scenario_id"] == scenario
        ]

        for metric in METRICS:
            omnibus = friedman_lookup.loc[(scenario, metric)]

            friedman_p_adjusted = float(
                omnibus["p_adjusted_holm"]
            )

            friedman_significant = bool(
                omnibus["significant"]
            )

            comparisons = []

            for scheduler_a, scheduler_b in combinations(
                SCHEDULERS, 2
            ):
                data_a = (
                    scenario_data[
                        scenario_data["scheduler"] == scheduler_a
                    ]
                    .set_index("seed")[metric]
                )

                data_b = (
                    scenario_data[
                        scenario_data["scheduler"] == scheduler_b
                    ]
                    .set_index("seed")[metric]
                )

                paired = pd.concat(
                    [data_a, data_b],
                    axis=1,
                    keys=["A", "B"],
                    join="inner",
                ).sort_index()

                if len(paired) != EXPECTED_SEEDS:
                    raise ValueError(
                        f"Invalid paired sample: "
                        f"{scenario}, {metric}, "
                        f"{scheduler_a} vs {scheduler_b}"
                    )

                a = paired["A"].to_numpy(dtype=float)
                b = paired["B"].to_numpy(dtype=float)

                differences = a - b

                if np.all(differences == 0):
                    statistic = 0.0
                    p_value = 1.0
                else:
                    test = wilcoxon(
                        differences,
                        alternative="two-sided",
                        method="auto",
                        zero_method="wilcox",
                    )

                    statistic = float(test.statistic)
                    p_value = float(test.pvalue)

                ci_lower, ci_upper = bootstrap_mean_ci(
                    differences,
                    rng,
                )

                comparisons.append({
                    "scenario_id": scenario,
                    "metric": metric,
                    "scheduler_a": scheduler_a,
                    "scheduler_b": scheduler_b,
                    "paired_seeds": len(paired),
                    "mean_a": float(a.mean()),
                    "mean_b": float(b.mean()),
                    "mean_difference_a_minus_b": float(
                        differences.mean()
                    ),
                    "ci_95_lower": ci_lower,
                    "ci_95_upper": ci_upper,
                    "wilcoxon_statistic": statistic,
                    "p_value": p_value,
                    "effect_size_rank_biserial": (
                        calculate_effect_size(a, b)
                    ),
                    "friedman_p_adjusted_holm": (
                        friedman_p_adjusted
                    ),
                    "friedman_significant": (
                        friedman_significant
                    ),
                })

            # Holm correction within each scenario-metric
            # family of three pairwise comparisons.
            adjusted_p = holm_correction([
                item["p_value"] for item in comparisons
            ])

            for item, corrected_p in zip(
                comparisons,
                adjusted_p,
            ):
                item["p_adjusted_holm"] = corrected_p

                item["pairwise_significant"] = (
                    corrected_p < ALPHA
                )

                # Confirmatory post-hoc interpretation requires
                # a significant corrected Friedman omnibus test.
                item["significant"] = (
                    item["friedman_significant"]
                    and item["pairwise_significant"]
                )

                records.append(item)

    return pd.DataFrame(records)


def main():
    print("=" * 70)
    print("PAIRED STATISTICAL SIGNIFICANCE ANALYSIS")
    print("=" * 70)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results = load_results()

    print(f"Experiments loaded: {len(results)}")
    print(f"Scenarios: {results['scenario_id'].nunique()}")
    print(f"Schedulers: {len(SCHEDULERS)}")
    print(f"Seeds per scheduler: {EXPECTED_SEEDS}")

    friedman_results = run_friedman_tests(results)

    pairwise_results = run_pairwise_tests(
        results,
        friedman_results,
    )

    friedman_results.to_csv(
        FRIEDMAN_OUTPUT_FILE,
        index=False,
    )

    pairwise_results.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nFRIEDMAN OMNIBUS TESTS")
    print("=" * 70)

    print(
        friedman_results[
            [
                "scenario_id",
                "metric",
                "friedman_statistic",
                "p_value",
                "p_adjusted_holm",
                "kendall_w",
                "significant",
            ]
        ].to_string(
            index=False,
            float_format=lambda value: f"{value:.8g}",
        )
    )

    print("\nMAKESPAN POST-HOC TESTS")
    print("=" * 70)

    makespan_results = pairwise_results[
        pairwise_results["metric"] == "makespan"
    ]

    display_columns = [
        "scenario_id",
        "scheduler_a",
        "scheduler_b",
        "mean_difference_a_minus_b",
        "ci_95_lower",
        "ci_95_upper",
        "p_adjusted_holm",
        "effect_size_rank_biserial",
        "friedman_significant",
        "significant",
    ]

    print(
        makespan_results[display_columns].to_string(
            index=False,
            float_format=lambda value: f"{value:.6g}",
        )
    )

    print("\n" + "=" * 70)
    print("STATISTICAL ANALYSIS SUMMARY")
    print("=" * 70)

    print(
        "Friedman tests:",
        len(friedman_results),
    )

    print(
        "Significant Friedman tests after global Holm:",
        int(friedman_results["significant"].sum()),
    )

    print(
        "Pairwise Wilcoxon tests:",
        len(pairwise_results),
    )

    print(
        "Significant pairwise tests after omnibus gating:",
        int(pairwise_results["significant"].sum()),
    )

    print(f"\nFriedman results: {FRIEDMAN_OUTPUT_FILE}")
    print(f"Pairwise results: {OUTPUT_FILE}")

    print("=" * 70)


if __name__ == "__main__":
    main()