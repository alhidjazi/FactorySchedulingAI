from dataclasses import dataclass

from baselines.base import BaseScheduler
from baselines.edd import EDDScheduler
from baselines.fifo import FIFOScheduler
from baselines.runner import SchedulingRunner
from baselines.spt import SPTScheduler
from experiments.scenarios import ScenarioConfig, build_factory
from factory_sim.metrics import SimulationMetrics
from factory_sim.simulation import SimulationEngine


@dataclass(frozen=True)
class BenchmarkResult:
    scenario_id: str
    seed: int
    scheduler: str
    makespan: float
    mean_flow_time: float
    total_tardiness: float
    mean_tardiness: float
    overall_machine_utilization: float
    machine_utilization: dict[str, float]


def run_benchmark(
    config: ScenarioConfig,
) -> list[BenchmarkResult]:
    """Run all baseline schedulers on the same scenario."""

    scheduler_factories: list[
        tuple[str, type[BaseScheduler]]
    ] = [
        ("FIFO", FIFOScheduler),
        ("SPT", SPTScheduler),
        ("EDD", EDDScheduler),
    ]

    results = []

    for scheduler_name, scheduler_class in scheduler_factories:
        factory = build_factory(config)
        engine = SimulationEngine(factory)
        scheduler = scheduler_class()

        runner = SchedulingRunner(engine, scheduler)
        runner.run()

        metrics = SimulationMetrics.calculate(engine)

        results.append(
            BenchmarkResult(
                scenario_id=config.scenario_id,
                seed=config.seed,
                scheduler=scheduler_name,
                makespan=metrics.makespan,
                mean_flow_time=metrics.mean_flow_time,
                total_tardiness=metrics.total_tardiness,
                mean_tardiness=metrics.mean_tardiness,
                overall_machine_utilization=(
                    metrics.overall_machine_utilization
                ),
                machine_utilization=dict(
                    metrics.machine_utilization
                ),
            )
        )

    return results