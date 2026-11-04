import pytest

from baselines.edd import EDDScheduler
from baselines.fifo import FIFOScheduler
from baselines.spt import SPTScheduler
from factory_sim.enums import MachineStatus
from factory_sim.job import Job
from factory_sim.machine import Machine
from factory_sim.operation import Operation


@pytest.fixture
def machines():
    return [
        Machine("M1"),
        Machine("M2"),
    ]


def create_job(
    job_id: str,
    release_time: float,
    due_date: float,
    processing_times: dict[str, float],
) -> Job:
    operation = Operation(
        operation_id=f"{job_id}-OP1",
        processing_times=processing_times,
    )

    return Job(
        job_id=job_id,
        release_time=release_time,
        due_date=due_date,
        operations=[operation],
    )


def test_fifo_selects_earliest_released_job(machines):
    jobs = [
        create_job("J2", 2, 20, {"M1": 3}),
        create_job("J1", 1, 30, {"M1": 5}),
    ]

    decision = FIFOScheduler().make_decision(
        jobs, machines, current_time=5
    )

    assert decision.job_id == "J1"
    assert decision.machine_id == "M1"


def test_spt_selects_shortest_processing_time(machines):
    jobs = [
        create_job("J1", 0, 20, {"M1": 8}),
        create_job("J2", 0, 30, {"M1": 3}),
    ]

    decision = SPTScheduler().make_decision(
        jobs, machines, current_time=0
    )

    assert decision.job_id == "J2"


def test_edd_selects_earliest_due_date(machines):
    jobs = [
        create_job("J1", 0, 30, {"M1": 2}),
        create_job("J2", 0, 15, {"M1": 8}),
    ]

    decision = EDDScheduler().make_decision(
        jobs, machines, current_time=0
    )

    assert decision.job_id == "J2"


def test_scheduler_ignores_unreleased_jobs(machines):
    jobs = [
        create_job("J1", 10, 20, {"M1": 1}),
        create_job("J2", 0, 30, {"M1": 5}),
    ]

    decision = FIFOScheduler().make_decision(
        jobs, machines, current_time=5
    )

    assert decision.job_id == "J2"


def test_scheduler_ignores_completed_jobs(machines):
    job = create_job("J1", 0, 20, {"M1": 3})
    job.current_operation_index = 1

    decision = FIFOScheduler().make_decision(
        [job], machines, current_time=5
    )

    assert decision is None


def test_scheduler_ignores_busy_machines(machines):
    machines[0].status = MachineStatus.BUSY

    jobs = [
        create_job("J1", 0, 20, {"M1": 3, "M2": 5}),
    ]

    decision = FIFOScheduler().make_decision(
        jobs, machines, current_time=0
    )

    assert decision.machine_id == "M2"


def test_scheduler_ignores_ineligible_machines():
    machines = [
        Machine("M1"),
        Machine("M2"),
    ]

    jobs = [
        create_job("J1", 0, 20, {"M1": 3}),
    ]

    decision = FIFOScheduler().make_decision(
        jobs, machines, current_time=0
    )

    assert decision.machine_id == "M1"


def test_scheduler_returns_none_without_available_machine():
    machine = Machine("M1")
    machine.status = MachineStatus.BUSY

    job = create_job("J1", 0, 20, {"M1": 3})

    decision = FIFOScheduler().make_decision(
        [job], [machine], current_time=0
    )

    assert decision is None


def test_spt_selects_fastest_eligible_machine():
    machines = [
        Machine("M1"),
        Machine("M2"),
    ]

    job = create_job(
        "J1",
        0,
        20,
        {"M1": 8, "M2": 3},
    )

    decision = SPTScheduler().make_decision(
        [job], machines, current_time=0
    )

    assert decision.machine_id == "M2"


def test_edd_uses_due_date_before_processing_time(machines):
    jobs = [
        create_job("J1", 0, 10, {"M1": 8}),
        create_job("J2", 0, 20, {"M1": 2}),
    ]

    decision = EDDScheduler().make_decision(
        jobs, machines, current_time=0
    )

    assert decision.job_id == "J1"


def test_fifo_is_deterministic(machines):
    jobs = [
        create_job("J2", 0, 20, {"M1": 3}),
        create_job("J1", 0, 20, {"M1": 3}),
    ]

    decision = FIFOScheduler().make_decision(
        jobs, machines, current_time=0
    )

    assert decision.job_id == "J1"
