from math import isfinite

import simpy

from factory_sim.enums import MachineStatus
from factory_sim.factory import Factory


class SimulationEngine:
    def __init__(self, factory: Factory):
        self.factory = factory
        self.env = simpy.Environment()

        self.event_log: list[dict[str, str | float]] = []

        self._reserved_machines: set[str] = set()
        self._reserved_jobs: set[str] = set()

        self._breakdown_events: dict[str, simpy.Event] = {}
        self._scheduled_breakdowns: set[str] = set()

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

    def schedule_breakdown(
        self,
        machine_id: str,
        breakdown_time: float,
        repair_time: float,
    ):
        """Schedule one deterministic breakdown at an absolute time."""
        machine = self.factory.get_machine(machine_id)

        if not isfinite(breakdown_time):
            raise ValueError("Breakdown time must be finite.")

        if breakdown_time < self.current_time:
            raise ValueError("Breakdown time cannot be in the past.")

        if not isfinite(repair_time) or repair_time <= 0:
            raise ValueError("Repair time must be finite and positive.")

        if machine_id in self._scheduled_breakdowns:
            raise RuntimeError(
                f"A breakdown is already scheduled for {machine_id}."
            )

        if machine.status == MachineStatus.DOWN:
            raise RuntimeError(f"Machine {machine_id} is already down.")

        self._scheduled_breakdowns.add(machine_id)
        breakdown_event = self.env.event()
        self._breakdown_events[machine_id] = breakdown_event

        return self.env.process(
            self._trigger_breakdown(
                machine_id,
                breakdown_time,
                repair_time,
                breakdown_event,
            )
        )

    def _trigger_breakdown(
        self,
        machine_id: str,
        breakdown_time: float,
        repair_time: float,
        breakdown_event: simpy.Event,
    ):
        yield self.env.timeout(breakdown_time - self.current_time)

        # Arıza planı iptal edilmişse zamanlayıcı işlem yapmamalı.
        if self._breakdown_events.get(machine_id) is not breakdown_event:
            return
        
        machine = self.factory.get_machine(machine_id)

        if machine.status != MachineStatus.BUSY:
            self._scheduled_breakdowns.discard(machine_id)
            self._breakdown_events.pop(machine_id, None)
            return

        breakdown_event.succeed(repair_time)

    def schedule_operation(self, job_id: str, machine_id: str):
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

        # Makineyi yalnızca Job üretime başlayabilecekse rezerve et.
        if self.current_time >= job.release_time:
            if (
                not machine.is_available
                or machine_id in self._reserved_machines
            ):
                raise RuntimeError(
                    f"Machine {machine_id} is not available."
                )

            self._reserved_machines.add(machine_id)

        self._reserved_jobs.add(job_id)

        return self.env.process(
            self._run_single_operation(job_id, machine_id)
        )

    def _run_single_operation(self, job_id: str, machine_id: str):
        try:
            job = self.factory.get_job(job_id)
            machine = self.factory.get_machine(machine_id)

            # Job'ın üretime başlayabileceği zamanı bekle.
            if self.current_time < job.release_time:
                yield self.env.timeout(
                    job.release_time - self.current_time
                )

            # Daha önce rezerve edilmemişse şimdi rezerve et.
            if machine_id not in self._reserved_machines:
                if (
                    not machine.is_available
                    or machine_id in self._reserved_machines
                ):
                    raise RuntimeError(
                        f"Machine {machine_id} is not available."
                    )

                self._reserved_machines.add(machine_id)

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
        """Schedule all remaining operations of a job sequentially."""
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

        if set(machine_assignments) != required_operation_ids:
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

                # İlk operasyon için release time beklenir.
                if self.current_time < job.release_time:
                    yield self.env.timeout(
                        job.release_time - self.current_time
                    )

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

        remaining_time = operation.get_processing_time(machine_id)

        machine.start_operation(job_id, operation.operation_id)

        self._record_event(
            "operation_started",
            machine_id,
            job_id,
            operation.operation_id,
        )

        last_segment_time = 0.0

        while remaining_time > 0:
            segment_start = self.current_time

            breakdown_event = self._breakdown_events.get(machine_id)

            if breakdown_event is None:
                last_segment_time = remaining_time
                yield self.env.timeout(remaining_time)
                break

            result = yield (
                self.env.timeout(remaining_time) | breakdown_event
            )

            elapsed = self.current_time - segment_start
            remaining_time = max(0.0, remaining_time - elapsed)
            last_segment_time = elapsed

            # Operasyon tamamlandıysa arıza kontrolüne gerek yok.
            # Aynı anda gerçekleşen olaylarda operasyon tamamlanmasına öncelik verilir.
            if remaining_time <= 0:
                # Operasyon tamamlandı: aynı zamana denk gelen arızayı iptal et.
                self._breakdown_events.pop(machine_id, None)
                self._scheduled_breakdowns.discard(machine_id)
                break

            if breakdown_event not in result:
                break

            # Arıza öncesinde gerçekleşen üretim süresini kaydet.
            machine.total_busy_time += elapsed

            repair_time = result[breakdown_event]

            machine.set_down()

            self._record_event(
                "machine_breakdown",
                machine_id,
                job_id,
                operation.operation_id,
            )

            self._record_event(
                "repair_started",
                machine_id,
                job_id,
                operation.operation_id,
            )

            yield self.env.timeout(repair_time)

            machine.repair(repair_time)

            self._record_event(
                "repair_completed",
                machine_id,
                job_id,
                operation.operation_id,
            )

            self._breakdown_events.pop(machine_id, None)
            self._scheduled_breakdowns.discard(machine_id)

        # Yalnızca son üretim segmentini kaydet.
        machine.finish_operation(last_segment_time)

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
