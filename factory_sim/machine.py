from dataclasses import dataclass
from math import isfinite

from factory_sim.enums import MachineStatus


@dataclass
class Machine:
    machine_id: str
    status: MachineStatus = MachineStatus.IDLE

    current_job_id: str | None = None
    current_operation_id: str | None = None
    current_setup_family: str | None = None

    status_before_down: MachineStatus | None = None

    total_busy_time: float = 0.0
    total_setup_time: float = 0.0
    total_down_time: float = 0.0

    def __post_init__(self):
        if not self.machine_id.strip():
            raise ValueError("machine_id cannot be empty.")

        self.validate_time_counters()

    @property
    def is_available(self) -> bool:
        return self.status == MachineStatus.IDLE

    def validate_time_counters(self):
        for name in (
            "total_busy_time",
            "total_setup_time",
            "total_down_time",
        ):
            value = getattr(self, name)

            if not isfinite(value) or value < 0:
                raise ValueError(f"{name} must be non-negative.")

    def start_operation(self, job_id: str, operation_id: str):
        if not self.is_available:
            raise RuntimeError(
                f"Machine {self.machine_id} is not available."
            )

        if not job_id.strip() or not operation_id.strip():
            raise ValueError("Job and operation IDs cannot be empty.")

        self.status = MachineStatus.BUSY
        self.current_job_id = job_id
        self.current_operation_id = operation_id

    def finish_operation(self, processing_time: float):
        if self.status != MachineStatus.BUSY:
            raise RuntimeError("Machine is not processing.")

        if not isfinite(processing_time) or processing_time <= 0:
            raise ValueError("Processing time must be positive.")

        self.total_busy_time += processing_time
        self.current_job_id = None
        self.current_operation_id = None
        self.status = MachineStatus.IDLE

    def set_down(self):
        if self.status not in (
            MachineStatus.IDLE,
            MachineStatus.BUSY,
        ):
            raise RuntimeError("Machine cannot enter DOWN state.")

        self.status_before_down = self.status
        self.status = MachineStatus.DOWN

    def repair(self, repair_time: float):
        if self.status != MachineStatus.DOWN:
            raise RuntimeError("Machine is not down.")

        if not isfinite(repair_time) or repair_time <= 0:
            raise ValueError("Repair time must be positive.")

        self.total_down_time += repair_time

        self.status = self.status_before_down or MachineStatus.IDLE
        self.status_before_down = None
