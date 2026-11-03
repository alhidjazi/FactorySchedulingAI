from dataclasses import dataclass, field

from factory_sim.job import Job
from factory_sim.machine import Machine


@dataclass
class Factory:
    factory_id: str

    machines: dict[str, Machine] = field(default_factory=dict)
    jobs: dict[str, Job] = field(default_factory=dict)

    def __post_init__(self):
        if not self.factory_id.strip():
            raise ValueError("factory_id cannot be empty.")

    def add_machine(self, machine: Machine):
        if machine.machine_id in self.machines:
            raise ValueError(
                f"Machine {machine.machine_id} already exists."
            )

        self.machines[machine.machine_id] = machine

    def add_job(self, job: Job):
        if job.job_id in self.jobs:
            raise ValueError(
                f"Job {job.job_id} already exists."
            )

        self.jobs[job.job_id] = job

    def get_machine(self, machine_id: str) -> Machine:
        try:
            return self.machines[machine_id]
        except KeyError:
            raise ValueError(
                f"Machine {machine_id} not found."
            ) from None

    def get_job(self, job_id: str) -> Job:
        try:
            return self.jobs[job_id]
        except KeyError:
            raise ValueError(
                f"Job {job_id} not found."
            ) from None

    @property
    def available_machines(self) -> list[Machine]:
        return [
            machine
            for machine in self.machines.values()
            if machine.is_available
        ]

    @property
    def machine_count(self) -> int:
        return len(self.machines)

    @property
    def job_count(self) -> int:
        return len(self.jobs)