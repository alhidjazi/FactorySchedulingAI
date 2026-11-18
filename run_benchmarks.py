from experiments.benchmark import run_benchmark
from experiments.results import save_results
from experiments.scenarios import ScenarioConfig

SEEDS = [
    42, 123, 456, 789, 2026,
    1001, 1002, 1003, 1004, 1005,
    1006, 1007, 1008, 1009, 1010,
    1011, 1012, 1013, 1014, 1015,
    1016, 1017, 1018, 1019, 1020,
    1021, 1022, 1023, 1024, 1025,
]

SCENARIOS = [
    {
        "scenario_id": "baseline_10x3",
        "job_count": 10,
        "machine_count": 3,
    },
    {
        "scenario_id": "baseline_25x3",
        "job_count": 25,
        "machine_count": 3,
    },
    {
        "scenario_id": "baseline_50x3",
        "job_count": 50,
        "machine_count": 3,
    },
]


for scenario in SCENARIOS:
    print(f"\n{'=' * 50}")
    print(f"Scenario: {scenario['scenario_id']}")
    print(f"{'=' * 50}")

    all_results = []
    first_config = None

    for seed in SEEDS:
        config = ScenarioConfig(
            scenario_id=scenario["scenario_id"],
            job_count=scenario["job_count"],
            machine_count=scenario["machine_count"],
            seed=seed,
        )

        if first_config is None:
            first_config = config

        print(f"\nRunning seed: {seed}")

        results = run_benchmark(config)
        all_results.extend(results)

        for result in results:
            print(
                f"{result.scheduler}: "
                f"Makespan={result.makespan:.2f}, "
                f"Mean Flow Time={result.mean_flow_time:.2f}, "
                f"Total Tardiness={result.total_tardiness:.2f}"
            )

    output_path = (
        f"results/{scenario['scenario_id']}.csv"
    )

    save_results(
        config=first_config,
        results=all_results,
        output_path=output_path,
    )

    print(f"\nSaved: {output_path}")
    print(f"Total results: {len(all_results)}")

print("\nAll multi-seed benchmark experiments completed.")