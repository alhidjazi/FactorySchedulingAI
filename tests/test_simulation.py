import pytest

from factory_sim.factory import Factory
from factory_sim.job import Job
from factory_sim.machine import Machine
from factory_sim.operation import Operation
from factory_sim.simulation import SimulationEngine


def create_test_factory() -> Factory:
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


def test_simulation_initialization():
    factory = create_test_factory()
    engine = SimulationEngine(factory)

    assert engine.current_time == 0
    assert engine.event_log == []


def test_single_operation_simulation():
    factory = create_test_factory()
    engine = SimulationEngine(factory)

    engine.schedule_operation("J1", "M1")
    engine.run()

    machine = factory.get_machine("M1")
    job = factory.get_job("J1")

    assert engine.current_time == 10.0
    assert machine.total_busy_time == 10.0
    assert machine.is_available
    assert job.is_completed


def test_operation_event_logging():
    factory = create_test_factory()
    engine = SimulationEngine(factory)

    engine.schedule_operation("J1", "M1")
    engine.run()

    assert len(engine.event_log) == 2

    start_event, complete_event = engine.event_log

    assert start_event["event"] == "operation_started"
    assert start_event["time"] == 0

    assert complete_event["event"] == "operation_completed"
    assert complete_event["time"] == 10.0


def test_simulation_rejects_ineligible_machine():
    factory = create_test_factory()
    factory.add_machine(Machine("M2"))

    engine = SimulationEngine(factory)

    with pytest.raises(ValueError):
        engine.schedule_operation("J1", "M2")


def test_simulation_rejects_completed_job():
    factory = create_test_factory()
    engine = SimulationEngine(factory)

    engine.schedule_operation("J1", "M1")
    engine.run()

    with pytest.raises(RuntimeError):
        engine.schedule_operation("J1", "M1")


def test_simulation_rejects_busy_machine():
    factory = create_test_factory()

    factory.add_job(
        Job(
            job_id="J2",
            release_time=0.0,
            due_date=40.0,
            operations=[
                Operation("O2", {"M1": 5.0}),
            ],
        )
    )

    engine = SimulationEngine(factory)

    engine.schedule_operation("J1", "M1")

    with pytest.raises(RuntimeError):
        engine.schedule_operation("J2", "M1")



def create_multi_operation_factory() -> Factory:
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

    return factory


def test_multi_operation_job_simulation():
    factory = create_multi_operation_factory()
    engine = SimulationEngine(factory)

    engine.schedule_job(
        "J1",
        {
            "O1": "M1",
            "O2": "M2",
            "O3": "M1",
        },
    )

    engine.run()

    job = factory.get_job("J1")

    assert job.is_completed
    assert job.remaining_operations == 0
    assert engine.current_time == 30.0


def test_multi_operation_sequence():
    factory = create_multi_operation_factory()
    engine = SimulationEngine(factory)

    engine.schedule_job(
        "J1",
        {
            "O1": "M1",
            "O2": "M2",
            "O3": "M1",
        },
    )

    engine.run()

    assert [
        (event["event"], event["operation_id"], event["time"])
        for event in engine.event_log
    ] == [
        ("operation_started", "O1", 0),
        ("operation_completed", "O1", 10.0),
        ("operation_started", "O2", 10.0),
        ("operation_completed", "O2", 25.0),
        ("operation_started", "O3", 25.0),
        ("operation_completed", "O3", 30.0),
    ]


def test_multi_operation_machine_busy_time():
    factory = create_multi_operation_factory()
    engine = SimulationEngine(factory)

    engine.schedule_job(
        "J1",
        {
            "O1": "M1",
            "O2": "M2",
            "O3": "M1",
        },
    )

    engine.run()

    assert factory.get_machine("M1").total_busy_time == 15.0
    assert factory.get_machine("M2").total_busy_time == 15.0


def test_schedule_job_rejects_missing_machine_assignment():
    factory = create_multi_operation_factory()
    engine = SimulationEngine(factory)

    with pytest.raises(ValueError):
        engine.schedule_job(
            "J1",
            {
                "O1": "M1",
                "O2": "M2",
            },
        )


def test_schedule_job_rejects_ineligible_machine():
    factory = create_multi_operation_factory()
    engine = SimulationEngine(factory)

    with pytest.raises(ValueError):
        engine.schedule_job(
            "J1",
            {
                "O1": "M2",
                "O2": "M2",
                "O3": "M1",
            },
        )


def test_schedule_job_rejects_duplicate_scheduling():
    factory = create_multi_operation_factory()
    engine = SimulationEngine(factory)

    engine.schedule_job(
        "J1",
        {
            "O1": "M1",
            "O2": "M2",
            "O3": "M1",
        },
    )

    with pytest.raises(RuntimeError):
        engine.schedule_job(
            "J1",
            {
                "O1": "M1",
                "O2": "M2",
                "O3": "M1",
            },
        )
