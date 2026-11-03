from dataclasses import dataclass, field
from math import isfinite

from factory_sim.operation import Operation


@dataclass
class Job:
    job_id: str
    release_time: float
    due_date: float
    operations: list[Operation]
    priority: int = 1
    current_operation_index: int = 0

    completed_operation_ids: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.job_id.strip():
            raise ValueError("job_id cannot be empty.")

        if not isfinite(self.release_time) or self.release_time < 0:
            raise ValueError("release_time must be finite and non-negative.")

        if not isfinite(self.due_date):
            raise ValueError("due_date must be finite.")

        if not self.operations:
            raise ValueError("A job must contain at least one operation.")

        if self.priority < 1:
            raise ValueError("priority must be at least 1.")

        if not 0 <= self.current_operation_index <= len(self.operations):
            raise ValueError("Invalid current_operation_index.")

        operation_ids = [
            operation.operation_id for operation in self.operations
        ]

        if len(operation_ids) != len(set(operation_ids)):
            raise ValueError(
                f"Duplicate operation IDs found in job {self.job_id}."
            )

    @property
    def current_operation(self) -> Operation | None:
        if self.is_completed:
            return None

        return self.operations[self.current_operation_index]

    @property
    def is_completed(self) -> bool:
        return self.current_operation_index >= len(self.operations)

    @property
    def remaining_operations(self) -> int:
        return len(self.operations) - self.current_operation_index

    def complete_current_operation(self) -> Operation:
        if self.is_completed:
            raise RuntimeError(
                f"Job {self.job_id} has no remaining operations."
            )

        completed_operation = self.operations[
            self.current_operation_index
        ]

        self.completed_operation_ids.append(
            completed_operation.operation_id
        )

        self.current_operation_index += 1

        return completed_operation
