from dataclasses import dataclass
from math import isfinite
from typing import Mapping


@dataclass(frozen=True)
class Operation:
    operation_id: str
    processing_times: Mapping[str, float]
    setup_family: str = "default"

    def __post_init__(self):
        if not self.operation_id.strip():
            raise ValueError("operation_id cannot be empty.")

        if not self.processing_times:
            raise ValueError(
                "An operation must have at least one eligible machine."
            )

        for machine_id, duration in self.processing_times.items():
            if not machine_id.strip():
                raise ValueError("Machine ID cannot be empty.")

            if not isfinite(duration) or duration <= 0:
                raise ValueError(
                    f"Invalid processing time for {machine_id}: {duration}"
                )

        if not self.setup_family.strip():
            raise ValueError("setup_family cannot be empty.")

    @property
    def eligible_machines(self) -> tuple[str, ...]:
        return tuple(self.processing_times.keys())

    def get_processing_time(self, machine_id: str) -> float:
        try:
            return self.processing_times[machine_id]
        except KeyError:
            raise ValueError(
                f"Machine {machine_id} is not eligible "
                f"for operation {self.operation_id}."
            ) from None
