import random
from dataclasses import dataclass
from math import isfinite

from factory_sim.factory import Factory
from factory_sim.job import Job
from factory_sim.machine import Machine
from factory_sim.operation import Operation


@dataclass(frozen=True)
class ScenarioConfig:
    scenario_id: str = "baseline_10x3"
    job_count: int = 10
    machine_count: int = 3

    min_operations: int = 2
    max_operations: int = 4

    min_processing_time: int = 3
    max_processing_time: int = 12

    max_release_time: float = 20.0
    due_date_factor: float = 1.5

    seed: int = 42

    def __post_init__(self):
        if not self.scenario_id.strip():
            raise ValueError("scenario_id cannot be empty.")

        if self.job_count < 1:
            raise ValueError("job_count must be at least 1.")

        if self.machine_count < 1:
            raise ValueError("machine_count must be at least 1.")

        if self.min_operations < 1:
            raise ValueError("min_operations must be at least 1.")

        if self.max_operations < self.min_operations:
            raise ValueError(
                "max_operations cannot be less than min_operations."
            )

        if self.min_processing_time < 1:
            raise ValueError(
                "min_processing_time must be positive."
            )

        if self.max_processing_time < self.min_processing_time:
            raise ValueError(
                "max_processing_time cannot be less than "
                "min_processing_time."
            )

        if (
            not isfinite(self.max_release_time)
            or self.max_release_time < 0
        ):
            raise ValueError(
                "max_release_time must be finite and non-negative."
            )

        if (
            not isfinite(self.due_date_factor)
            or self.due_date_factor <= 0
        ):
            raise ValueError(
                "due_date_factor must be finite and positive."
            )


def build_factory(config: ScenarioConfig) -> Factory:
    """Build a reproducible factory from a scenario configuration."""

    rng = random.Random(config.seed)

    factory = Factory(factory_id=config.scenario_id)

    machine_ids = [
        f"M{i + 1}"
        for i in range(config.machine_count)
    ]

    for machine_id in machine_ids:
        factory.add_machine(Machine(machine_id))

    for job_index in range(config.job_count):
        job_id = f"J{job_index + 1}"

        release_time = round(
            rng.uniform(0, config.max_release_time),
            2,
        )

        operation_count = rng.randint(
            config.min_operations,
            config.max_operations,
        )

        operations = []
        minimum_total_processing_time = 0

        for operation_index in range(operation_count):
            operation_id = (
                f"{job_id}_O{operation_index + 1}"
            )

            processing_times = {
                machine_id: float(
                    rng.randint(
                        config.min_processing_time,
                        config.max_processing_time,
                    )
                )
                for machine_id in machine_ids
            }

            minimum_total_processing_time += min(
                processing_times.values()
            )

            operations.append(
                Operation(
                    operation_id=operation_id,
                    processing_times=processing_times,
                )
            )

        due_date = (
            release_time
            + minimum_total_processing_time
            * config.due_date_factor
        )

        factory.add_job(
            Job(
                job_id=job_id,
                release_time=release_time,
                due_date=round(due_date, 2),
                operations=operations,
            )
        )

    return factory