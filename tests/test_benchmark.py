from experiments.benchmark import run_benchmark
from experiments.scenarios import ScenarioConfig


def test_benchmark_runs_all_schedulers():
    config = ScenarioConfig(seed=42)

    results = run_benchmark(config)

    assert len(results) == 3

    assert {
        result.scheduler for result in results
    } == {"FIFO", "SPT", "EDD"}


def test_benchmark_uses_same_scenario():
    config = ScenarioConfig(seed=42)

    results = run_benchmark(config)

    assert all(
        result.scenario_id == config.scenario_id
        for result in results
    )


def test_benchmark_results_are_valid():
    config = ScenarioConfig(seed=42)

    results = run_benchmark(config)

    for result in results:
        assert result.makespan > 0
        assert result.mean_flow_time >= 0
        assert result.total_tardiness >= 0
        assert result.mean_tardiness >= 0

        assert 0 <= result.overall_machine_utilization <= 100

        assert len(result.machine_utilization) == (
            config.machine_count
        )

        assert all(
            0 <= utilization <= 100
            for utilization in result.machine_utilization.values()
        )


def test_benchmark_is_reproducible():
    config = ScenarioConfig(seed=42)

    first_results = run_benchmark(config)
    second_results = run_benchmark(config)

    assert first_results == second_results