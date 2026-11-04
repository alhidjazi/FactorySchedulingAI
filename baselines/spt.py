from baselines.base import BaseScheduler
from factory_sim.job import Job
from factory_sim.machine import Machine
from factory_sim.operation import Operation


class SPTScheduler(BaseScheduler):
    """Shortest Processing Time scheduling policy."""

    def priority_key(
        self,
        job: Job,
        operation: Operation,
        machine: Machine,
        _current_time: float,
    ) -> tuple[float | int | str, ...]:
        return (
            operation.get_processing_time(machine.machine_id),
            job.release_time,
            job.due_date,
            job.job_id,
            machine.machine_id,
        )