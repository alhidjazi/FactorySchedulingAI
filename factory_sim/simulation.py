import simpy

from factory_sim.factory import Factory


class SimulationEngine:
    def __init__(self, factory: Factory):
        self.factory = factory
        self.env = simpy.Environment()

        self._reserved_machines: set[str] = set()
        self.event_log: list[dict[str, str | float]] = []

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
        job = self.factory.get_job(job_id)
        machine = self.factory.get_machine(machine_id)

        operation = job.current_operation

        if operation is None:
            raise RuntimeError(
                f"Job {job_id} has no remaining operations."
            )

        if machine_id not in operation.eligible_machines:
            raise ValueError(
                f"Machine {machine_id} cannot process "
                f"operation {operation.operation_id}."
            )

        if not machine.is_available or machine_id in self._reserved_machines:
            raise RuntimeError(
                f"Machine {machine_id} is not available."
            )

        self._reserved_machines.add(machine_id)

        return self.env.process(
            self._process_operation(job_id, machine_id)
        )

    def _process_operation(self, job_id: str, machine_id: str):
        try:
            job = self.factory.get_job(job_id)
            machine = self.factory.get_machine(machine_id)

            operation = job.current_operation

            if operation is None:
                raise RuntimeError(
                    f"Job {job_id} has no remaining operations."
                )

            if not machine.is_available:
                raise RuntimeError(
                    f"Machine {machine_id} is not available."
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

        finally:
            self._reserved_machines.discard(machine_id)

    def run(self, until: float | None = None):
        if until is None:
            self.env.run()
        else:
            self.env.run(until=until)