import pytest

from baselines.fifo import FIFOScheduler
from baselines.runner import SchedulingRunner
from factory_sim.factory import Factory
from factory_sim.job import Job
from factory_sim.machine import Machine
from factory_sim.metrics import SimulationMetrics
from factory_sim.operation import Operation
from factory_sim.simulation import SimulationEngine


def create_test_simulation():
    factory = Factory("F1")

    factory.add_machine(Machine("M1"))

    factory.add_job(
        Job(
            job_id="J1",
            release_time=0,
            due_date=3,
            operations=[
                Operation(
                    "O1",
                    {"M1": 2},
                )
            ],
        )
    )

    factory.add_job(
        Job(
            job_id="J2",
            release_time=1,
            due_date=2,
            operations=[
                Operation(
                    "O2",
                    {"M1": 2},
                )
            ],
        )
    )

    engine = SimulationEngine(factory)

    return engine


def test_metrics_calculate_single_machine_simulation():
    engine = create_test_simulation()

    runner = SchedulingRunner(
        engine,
        FIFOScheduler(),
    )

    runner.run()

    metrics = SimulationMetrics.calculate(engine)

    assert metrics.makespan == pytest.approx(4.0)

    assert metrics.mean_flow_time == pytest.approx(2.5)

    assert metrics.total_tardiness == pytest.approx(2.0)

    assert metrics.mean_tardiness == pytest.approx(1.0)

    assert metrics.machine_utilization["M1"] == pytest.approx(
        100.0
    )

    assert metrics.overall_machine_utilization == pytest.approx(
        100.0
    )

    assert metrics.completion_times == {
        "J1": 2.0,
        "J2": 4.0,
    }


def test_metrics_reject_incomplete_jobs():
    engine = create_test_simulation()

    with pytest.raises(RuntimeError, match="all jobs complete"):
        SimulationMetrics.calculate(engine)


def test_metrics_reject_empty_factory():
    factory = Factory("F1")
    engine = SimulationEngine(factory)

    with pytest.raises(ValueError, match="without jobs"):
        SimulationMetrics.calculate(engine)


def test_metrics_reject_missing_completion_events():
    engine = create_test_simulation()

    runner = SchedulingRunner(
        engine,
        FIFOScheduler(),
    )

    runner.run()

    engine.event_log.clear()

    with pytest.raises(
        RuntimeError,
        match="Missing completion events",
    ):
        SimulationMetrics.calculate(engine)


def test_metrics_uses_final_operation_completion_time():
    factory = Factory("F1")

    factory.add_machine(Machine("M1"))
    factory.add_machine(Machine("M2"))

    factory.add_job(
        Job(
            job_id="J1",
            release_time=0,
            due_date=10,
            operations=[
                Operation("O1", {"M1": 2}),
                Operation("O2", {"M2": 3}),
            ],
        )
    )

    engine = SimulationEngine(factory)

    runner = SchedulingRunner(
        engine,
        FIFOScheduler(),
    )

    runner.run()

    metrics = SimulationMetrics.calculate(engine)

    assert metrics.completion_times["J1"] == pytest.approx(5.0)
    assert metrics.makespan == pytest.approx(5.0)
    assert metrics.mean_flow_time == pytest.approx(5.0)
    assert metrics.total_tardiness == pytest.approx(0.0)


def test_metrics_makespan_includes_initial_idle_time():
    factory = Factory("F1")
    factory.add_machine(Machine("M1"))

    factory.add_job(
        Job(
            job_id="J1",
            release_time=5,
            due_date=10,
            operations=[
                Operation("O1", {"M1": 2}),
            ],
        )
    )

    engine = SimulationEngine(factory)
    runner = SchedulingRunner(engine, FIFOScheduler())
    runner.run()

    metrics = SimulationMetrics.calculate(engine)

    assert metrics.completion_times["J1"] == pytest.approx(7.0)
    assert metrics.makespan == pytest.approx(7.0)
    assert metrics.mean_flow_time == pytest.approx(2.0)
    assert metrics.machine_utilization["M1"] == pytest.approx(
        200 / 7
    )