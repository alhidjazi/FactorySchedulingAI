import csv
from pathlib import Path

from experiments.benchmark import BenchmarkResult
from experiments.scenarios import ScenarioConfig


def save_results(
    config: ScenarioConfig,
    results: list[BenchmarkResult],
    output_path: str | Path,
) -> None:
    """Save benchmark results to a CSV file."""

    if not results:
        raise ValueError("Benchmark results cannot be empty.")

    if any(
        result.scenario_id != config.scenario_id
        for result in results
    ):
        raise ValueError(
            "All benchmark results must belong to the given scenario."
        )

    machine_ids = sorted(results[0].machine_utilization)

    for result in results:
        if set(result.machine_utilization) != set(machine_ids):
            raise ValueError(
                "All results must contain the same machine IDs."
            )

    fieldnames = [
        "scenario_id",
        "seed",
        "job_count",
        "machine_count",
        "scheduler",
        "makespan",
        "mean_flow_time",
        "total_tardiness",
        "mean_tardiness",
        "overall_machine_utilization",
        *[
            f"utilization_{machine_id}"
            for machine_id in machine_ids
        ],
    ]

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for result in results:
            row = {
                "scenario_id": result.scenario_id,
                "seed": result.seed,
                "job_count": config.job_count,
                "machine_count": config.machine_count,
                "scheduler": result.scheduler,
                "makespan": result.makespan,
                "mean_flow_time": result.mean_flow_time,
                "total_tardiness": result.total_tardiness,
                "mean_tardiness": result.mean_tardiness,
                "overall_machine_utilization": (
                    result.overall_machine_utilization
                ),
            }

            for machine_id in machine_ids:
                row[f"utilization_{machine_id}"] = (
                    result.machine_utilization[machine_id]
                )

            writer.writerow(row)