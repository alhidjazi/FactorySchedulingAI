import pytest

from baselines.fifo import FIFOScheduler
from baselines.runner import SchedulingRunner
from factory_sim.factory import Factory
from factory_sim.job import Job
from factory_sim.machine import Machine
from factory_sim.operation import Operation
from factory_sim.simulation import SimulationEngine


def create_single_operation_factory() -> Factory:
    factory = Factory("F1")
    factory.add_machine(Machine("M1"))

    factory.add_job(
        Job(
            job_id="J1",
            release_time=0.0,
            due_date=30.0,
            operations=[
                Operation("O1", {"M1": 10.0}),
            ],
        )
    )

    return factory


def test_runner_completes_single_operation():
    factory = create_single_operation_factory()
    engine = SimulationEngine(factory)

    runner = SchedulingRunner(engine, FIFOScheduler())
    runner.run()

    job = factory.get_job("J1")
    machine = factory.get_machine("M1")

    assert job.is_completed
    assert engine.current_time == 10.0
    assert machine.total_busy_time == 10.0
    assert machine.is_available


def test_runner_completes_sequential_operations():
    factory = Factory("F1")

    factory.add_machine(Machine("M1"))
    factory.add_machine(Machine("M2"))

    factory.add_job(
        Job(
            job_id="J1",
            release_time=0.0,
            due_date=50.0,
            operations=[
                Operation("O1", {"M1": 10.0}),
                Operation("O2", {"M2": 15.0}),
                Operation("O3", {"M1": 5.0}),
            ],
        )
    )

    engine = SimulationEngine(factory)
    runner = SchedulingRunner(engine, FIFOScheduler())

    runner.run()

    job = factory.get_job("J1")

    assert job.is_completed
    assert job.completed_operation_ids == ["O1", "O2", "O3"]
    assert engine.current_time == 30.0


def test_runner_dispatches_multiple_jobs():
    factory = Factory("F1")

    factory.add_machine(Machine("M1"))
    factory.add_machine(Machine("M2"))

    factory.add_job(
        Job(
            "J1",
            0.0,
            30.0,
            [Operation("O1", {"M1": 10.0})],
        )
    )

    factory.add_job(
        Job(
            "J2",
            0.0,
            30.0,
            [Operation("O2", {"M2": 15.0})],
        )
    )

    engine = SimulationEngine(factory)
    runner = SchedulingRunner(engine, FIFOScheduler())

    runner.run()

    assert factory.get_job("J1").is_completed
    assert factory.get_job("J2").is_completed
    assert engine.current_time == 15.0

    assert factory.get_machine("M1").total_busy_time == 10.0
    assert factory.get_machine("M2").total_busy_time == 15.0


def test_runner_respects_release_time():
    factory = Factory("F1")
    factory.add_machine(Machine("M1"))

    factory.add_job(
        Job(
            "J1",
            10.0,
            30.0,
            [Operation("O1", {"M1": 5.0})],
        )
    )

    engine = SimulationEngine(factory)
    runner = SchedulingRunner(engine, FIFOScheduler())

    runner.run()

    start_event = next(
        event
        for event in engine.event_log
        if event["event"] == "operation_started"
    )

    assert start_event["time"] == 10.0
    assert engine.current_time == 15.0


def test_runner_releases_machine_after_completion():
    factory = Factory("F1")
    factory.add_machine(Machine("M1"))

    for job_id, operation_id, duration in [
        ("J1", "O1", 10.0),
        ("J2", "O2", 5.0),
    ]:
        factory.add_job(
            Job(
                job_id,
                0.0,
                30.0,
                [Operation(operation_id, {"M1": duration})],
            )
        )

    engine = SimulationEngine(factory)
    runner = SchedulingRunner(engine, FIFOScheduler())

    runner.run()

    machine = factory.get_machine("M1")

    assert factory.get_job("J1").is_completed
    assert factory.get_job("J2").is_completed
    assert machine.total_busy_time == 15.0
    assert machine.is_available


def test_runner_detects_deadlock():
    factory = Factory("F1")
    factory.add_machine(Machine("M1"))

    factory.add_job(
        Job(
            "J1",
            0.0,
            30.0,
            [Operation("O1", {"M2": 10.0})],
        )
    )

    engine = SimulationEngine(factory)
    runner = SchedulingRunner(engine, FIFOScheduler())

    with pytest.raises(RuntimeError, match="deadlock"):
        runner.run()


def test_runner_can_only_run_once():
    factory = create_single_operation_factory()
    engine = SimulationEngine(factory)

    runner = SchedulingRunner(engine, FIFOScheduler())

    runner.run()

    with pytest.raises(RuntimeError, match="only be run once"):
        runner.run()


def test_runner_returns_simulation_engine():
    factory = create_single_operation_factory()
    engine = SimulationEngine(factory)

    runner = SchedulingRunner(engine, FIFOScheduler())

    result = runner.run()

    assert result is engine


def test_runner_records_operation_events():
    factory = create_single_operation_factory()
    engine = SimulationEngine(factory)

    runner = SchedulingRunner(engine, FIFOScheduler())
    runner.run()

    assert [
        (event["event"], event["operation_id"], event["time"])
        for event in engine.event_log
    ] == [
        ("operation_started", "O1", 0),
        ("operation_completed", "O1", 10.0),
    ]
