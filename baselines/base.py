from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass

from factory_sim.job import Job
from factory_sim.machine import Machine
from factory_sim.operation import Operation


@dataclass(frozen=True)
class SchedulingDecision:
    """Represents a scheduling decision for one operation."""

    job_id: str
    operation_id: str
    machine_id: str


class BaseScheduler(ABC):
    """Common interface for classical scheduling algorithms."""

    @abstractmethod
    def priority_key(
        self,
        job: Job,
        operation: Operation,
        machine: Machine,
        current_time: float,
    ) -> tuple[float | int | str, ...]:
        """Return the priority key for a feasible job-machine candidate."""
        raise NotImplementedError

    def make_decision(
        self,
        jobs: Iterable[Job],
        available_machines: Iterable[Machine],
        current_time: float,
    ) -> SchedulingDecision | None:
        """Select the highest-priority feasible job-machine pair."""

        candidates = []

        for job in jobs:
            if job.release_time > current_time or job.is_completed:
                continue

            operation = job.current_operation

            if operation is None:
                continue

            for machine in available_machines:
                if not machine.is_available:
                    continue

                if machine.machine_id not in operation.eligible_machines:
                    continue

                priority = self.priority_key(
                    job,
                    operation,
                    machine,
                    current_time,
                )

                candidates.append(
                    (priority, job, operation, machine)
                )

        if not candidates:
            return None

        _, job, operation, machine = min(
            candidates,
            key=lambda candidate: candidate[0],
        )

        return SchedulingDecision(
            job_id=job.job_id,
            operation_id=operation.operation_id,
            machine_id=machine.machine_id,
        )
