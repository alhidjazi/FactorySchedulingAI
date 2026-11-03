import pytest

from factory_sim.factory import Factory
from factory_sim.job import Job
from factory_sim.machine import Machine
from factory_sim.operation import Operation


def create_test_job(job_id: str = "J1") -> Job:
    return Job(
        job_id=job_id,
        release_time=0.0,
        due_date=30.0,
        operations=[
            Operation("O1", {"M1": 10.0}),
        ],
    )


def test_factory_creation():
    factory = Factory("F1")

    assert factory.factory_id == "F1"
    assert factory.machine_count == 0
    assert factory.job_count == 0


def test_factory_add_machine():
    factory = Factory("F1")
    machine = Machine("M1")

    factory.add_machine(machine)

    assert factory.machine_count == 1
    assert factory.get_machine("M1") is machine


def test_factory_rejects_duplicate_machine():
    factory = Factory("F1")

    factory.add_machine(Machine("M1"))

    with pytest.raises(ValueError):
        factory.add_machine(Machine("M1"))


def test_factory_add_job():
    factory = Factory("F1")
    job = create_test_job()

    factory.add_job(job)

    assert factory.job_count == 1
    assert factory.get_job("J1") is job


def test_factory_rejects_duplicate_job():
    factory = Factory("F1")

    factory.add_job(create_test_job())

    with pytest.raises(ValueError):
        factory.add_job(create_test_job())


def test_factory_available_machines():
    factory = Factory("F1")

    machine_1 = Machine("M1")
    machine_2 = Machine("M2")

    factory.add_machine(machine_1)
    factory.add_machine(machine_2)

    machine_1.start_operation("J1", "O1")

    available = factory.available_machines

    assert len(available) == 1
    assert available[0].machine_id == "M2"


def test_factory_get_unknown_machine():
    factory = Factory("F1")

    with pytest.raises(ValueError):
        factory.get_machine("M99")


def test_factory_get_unknown_job():
    factory = Factory("F1")

    with pytest.raises(ValueError):
        factory.get_job("J99")