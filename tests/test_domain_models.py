import pytest

from factory_sim.enums import MachineStatus
from factory_sim.job import Job
from factory_sim.machine import Machine
from factory_sim.operation import Operation


def test_operation_creation():
    operation = Operation(
        operation_id="O1",
        processing_times={
            "M1": 10.0,
            "M2": 12.0,
        },
    )

    assert operation.eligible_machines == ("M1", "M2")
    assert operation.get_processing_time("M1") == 10.0


def test_operation_rejects_invalid_processing_time():
    with pytest.raises(ValueError):
        Operation(
            operation_id="O1",
            processing_times={"M1": -5.0},
        )


def test_operation_rejects_ineligible_machine():
    operation = Operation(
        operation_id="O1",
        processing_times={"M1": 10.0},
    )

    with pytest.raises(ValueError):
        operation.get_processing_time("M2")


def test_job_operation_sequence():
    job = Job(
        job_id="J1",
        release_time=0.0,
        due_date=30.0,
        operations=[
            Operation("O1", {"M1": 10.0}),
            Operation("O2", {"M2": 15.0}),
        ],
    )

    assert job.current_operation.operation_id == "O1"
    assert job.remaining_operations == 2

    completed = job.complete_current_operation()

    assert completed.operation_id == "O1"
    assert job.current_operation.operation_id == "O2"
    assert job.remaining_operations == 1

    job.complete_current_operation()

    assert job.is_completed
    assert job.current_operation is None


def test_machine_operation_lifecycle():
    machine = Machine("M1")

    assert machine.is_available

    machine.start_operation("J1", "O1")

    assert machine.status == MachineStatus.BUSY
    assert machine.current_job_id == "J1"

    machine.finish_operation(10.0)

    assert machine.status == MachineStatus.IDLE
    assert machine.current_job_id is None
    assert machine.total_busy_time == 10.0


def test_machine_cannot_start_two_operations():
    machine = Machine("M1")

    machine.start_operation("J1", "O1")

    with pytest.raises(RuntimeError):
        machine.start_operation("J2", "O1")


def test_machine_breakdown_and_repair():
    machine = Machine("M1")

    machine.start_operation("J1", "O1")
    machine.set_down()

    assert machine.status == MachineStatus.DOWN
    assert machine.current_job_id == "J1"

    machine.repair(5.0)

    assert machine.status == MachineStatus.BUSY
    assert machine.current_job_id == "J1"
    assert machine.total_down_time == 5.0


def test_machine_rejects_invalid_repair_time():
    machine = Machine("M1")
    machine.set_down()

    with pytest.raises(ValueError):
        machine.repair(-5.0)
