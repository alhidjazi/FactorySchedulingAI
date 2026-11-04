from baselines.base import BaseScheduler
from factory_sim.job import Job
from factory_sim.machine import Machine
from factory_sim.operation import Operation


class EDDScheduler(BaseScheduler):
    """Earliest Due Date scheduling policy."""

    def priority_key(
        self,
        job: Job,
        operation: Operation,
        machine: Machine,
        _current_time: float,
    ) -> tuple[float | int | str, ...]:
        return (
            job.due_date,
            job.release_time,
            job.job_id,
            operation.get_processing_time(machine.machine_id),
            machine.machine_id,
        )