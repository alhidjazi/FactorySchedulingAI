import csv

import pytest

from experiments.benchmark import run_benchmark
from experiments.results import save_results
from experiments.scenarios import ScenarioConfig


def test_save_results_writes_csv(tmp_path):
    config = ScenarioConfig(seed=42)
    results = run_benchmark(config)

    output_path = tmp_path / "benchmark.csv"

    save_results(config, results, output_path)

    with output_path.open(encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 3
    assert {row["scheduler"] for row in rows} == {
        "FIFO",
        "SPT",
        "EDD",
    }

    assert all(row["seed"] == "42" for row in rows)
    assert all(row["job_count"] == "10" for row in rows)
    assert all(row["machine_count"] == "3" for row in rows)


def test_save_results_creates_parent_directory(tmp_path):
    config = ScenarioConfig(seed=42)
    results = run_benchmark(config)

    output_path = tmp_path / "nested" / "benchmark.csv"

    save_results(config, results, output_path)

    assert output_path.exists()


def test_save_results_rejects_empty_results(tmp_path):
    config = ScenarioConfig(seed=42)

    with pytest.raises(ValueError, match="cannot be empty"):
        save_results(config, [], tmp_path / "empty.csv")


def test_save_results_rejects_different_scenario(tmp_path):
    config = ScenarioConfig(seed=42)
    results = run_benchmark(config)

    different_config = ScenarioConfig(
        scenario_id="different_scenario",
        seed=42,
    )

    with pytest.raises(ValueError, match="given scenario"):
        save_results(
            different_config,
            results,
            tmp_path / "invalid.csv",
        )