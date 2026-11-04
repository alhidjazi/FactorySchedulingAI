import simpy

from factory_sim.factory import Factory


class SimulationEngine:
    def __init__(self, factory: Factory):
        self.factory = factory
        self.env = simpy.Environment()

        self.event_log: list[dict[str, str | float]] = []

        self._reserved_machines: set[str] = set()
        self._reserved_jobs: set[str] = set()

    @property
    def current_time(self) -> float:
        return self.env.now

    def _record_event(
        self,
        event_type: str,
        machine_id: str,
        job_id: str,
        operation_id: str,
    ):
        self.event_log.append(
            {
                "time": self.current_time,
                "event": event_type,
                "machine_id": machine_id,
                "job_id": job_id,
                "operation_id": operation_id,
            }
        )

    def schedule_operation(
        self,
        job_id: str,
        machine_id: str,
    ):
        """Schedule only the current operation of a job."""
        job = self.factory.get_job(job_id)
        machine = self.factory.get_machine(machine_id)

        operation = job.current_operation

        if operation is None:
            raise RuntimeError(
                f"Job {job_id} has no remaining operations."
            )

        if job_id in self._reserved_jobs:
            raise RuntimeError(
                f"Job {job_id} is already scheduled."
            )

        if machine_id not in operation.eligible_machines:
            raise ValueError(
                f"Machine {machine_id} cannot process "
                f"operation {operation.operation_id}."
            )

        if (
            not machine.is_available
            or machine_id in self._reserved_machines
        ):
            raise RuntimeError(
                f"Machine {machine_id} is not available."
            )

        self._reserved_jobs.add(job_id)
        self._reserved_machines.add(machine_id)

        return self.env.process(
            self._run_single_operation(job_id, machine_id)
        )

    def _run_single_operation(self, job_id: str, machine_id: str):
        try:
            yield self.env.process(
                self._execute_operation(job_id, machine_id)
            )
        finally:
            self._reserved_machines.discard(machine_id)
            self._reserved_jobs.discard(job_id)

    def schedule_job(
        self,
        job_id: str,
        machine_assignments: dict[str, str],
    ):
        """
        Schedule all remaining operations of a job sequentially.

        machine_assignments maps operation IDs to machine IDs.
        Example: {"O1": "M1", "O2": "M2"}
        """
        job = self.factory.get_job(job_id)

        if job.is_completed:
            raise RuntimeError(
                f"Job {job_id} has no remaining operations."
            )

        if job_id in self._reserved_jobs:
            raise RuntimeError(
                f"Job {job_id} is already scheduled."
            )

        remaining_operations = job.operations[
            job.current_operation_index:
        ]

        required_operation_ids = {
            operation.operation_id
            for operation in remaining_operations
        }

        supplied_operation_ids = set(machine_assignments)

        if supplied_operation_ids != required_operation_ids:
            raise ValueError(
                "Machine assignments must contain exactly "
                "the remaining operation IDs."
            )

        for operation in remaining_operations:
            machine_id = machine_assignments[operation.operation_id]

            if machine_id not in operation.eligible_machines:
                raise ValueError(
                    f"Machine {machine_id} cannot process "
                    f"operation {operation.operation_id}."
                )

            self.factory.get_machine(machine_id)

        self._reserved_jobs.add(job_id)

        return self.env.process(
            self._run_job(job_id, machine_assignments)
        )

    def _run_job(
        self,
        job_id: str,
        machine_assignments: dict[str, str],
    ):
        try:
            job = self.factory.get_job(job_id)

            while not job.is_completed:
                operation = job.current_operation
                machine_id = machine_assignments[
                    operation.operation_id
                ]
                machine = self.factory.get_machine(machine_id)

                if (
                    not machine.is_available
                    or machine_id in self._reserved_machines
                ):
                    raise RuntimeError(
                        f"Machine {machine_id} is not available."
                    )

                self._reserved_machines.add(machine_id)

                try:
                    yield self.env.process(
                        self._execute_operation(job_id, machine_id)
                    )
                finally:
                    self._reserved_machines.discard(machine_id)

        finally:
            self._reserved_jobs.discard(job_id)

    def _execute_operation(self, job_id: str, machine_id: str):
        job = self.factory.get_job(job_id)
        machine = self.factory.get_machine(machine_id)

        operation = job.current_operation

        if operation is None:
            raise RuntimeError(
                f"Job {job_id} has no remaining operations."
            )

        processing_time = operation.get_processing_time(machine_id)

        machine.start_operation(job_id, operation.operation_id)

        self._record_event(
            "operation_started",
            machine_id,
            job_id,
            operation.operation_id,
        )

        yield self.env.timeout(processing_time)

        machine.finish_operation(processing_time)
        job.complete_current_operation()

        self._record_event(
            "operation_completed",
            machine_id,
            job_id,
            operation.operation_id,
        )

    def run(self, until: float | None = None):
        if until is None:
            self.env.run()
        else:
            self.env.run(until=until)