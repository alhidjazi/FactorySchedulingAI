import simpy

from baselines.base import BaseScheduler
from factory_sim.simulation import SimulationEngine


class SchedulingRunner:
    """Coordinates scheduling decisions and simulation events."""

    def __init__(
        self,
        engine: SimulationEngine,
        scheduler: BaseScheduler,
    ):
        self.engine = engine
        self.scheduler = scheduler

        self._active_processes: dict[str, simpy.Process] = {}
        self._job_machines: dict[str, str] = {}
        self._active_machines: set[str] = set()
        self._active_jobs: set[str] = set()

        self._release_events: dict[str, simpy.Event] = {}

        self._started = False

    def _schedule_release_events(self):
        """Create events for jobs that have not been released yet."""

        for job in self.engine.factory.jobs.values():
            if job.is_completed:
                continue

            if job.job_id in self._active_jobs:
                continue

            if job.job_id in self._release_events:
                continue

            if job.release_time > self.engine.current_time:
                self._release_events[job.job_id] = (
                    self.engine.env.timeout(
                        job.release_time - self.engine.current_time
                    )
                )

    def _dispatch_available_operations(self):
        """Dispatch feasible operations until no assignment is possible."""

        while True:
            current_time = self.engine.current_time

            available_jobs = [
                job
                for job in self.engine.factory.jobs.values()
                if (
                    not job.is_completed
                    and job.job_id not in self._active_jobs
                    and job.release_time <= current_time
                )
            ]

            available_machines = [
                machine
                for machine in self.engine.factory.available_machines
                if machine.machine_id not in self._active_machines
            ]

            if not available_jobs or not available_machines:
                return

            decision = self.scheduler.make_decision(
                jobs=available_jobs,
                available_machines=available_machines,
                current_time=current_time,
            )

            if decision is None:
                return

            job = self.engine.factory.get_job(decision.job_id)
            machine = self.engine.factory.get_machine(
                decision.machine_id
            )

            operation = job.current_operation

            if (
                operation is None
                or operation.operation_id != decision.operation_id
            ):
                raise RuntimeError(
                    "Scheduling decision does not match "
                    "the current operation."
                )

            process = self.engine.schedule_operation(
                job_id=decision.job_id,
                machine_id=decision.machine_id,
            )

            self._active_processes[job.job_id] = process
            
            self._active_jobs.add(job.job_id)
            self._active_machines.add(machine.machine_id)
            
            self._job_machines[job.job_id] = machine.machine_id

    def _cleanup_completed_processes(self):
        """Remove completed processes and release reservations."""

        completed_jobs = [
            job_id
            for job_id, process in self._active_processes.items()
            if process.processed
        ]

        for job_id in completed_jobs:
            process = self._active_processes.pop(job_id)

            if not process.ok:
                raise process.value

            machine_id = self._job_machines.pop(job_id)

            self._active_jobs.discard(job_id)
            self._active_machines.discard(machine_id)

    def _cleanup_release_events(self):
        """Remove release events that have already been processed."""

        released_jobs = [
            job_id
            for job_id, event in self._release_events.items()
            if event.processed
        ]

        for job_id in released_jobs:
            self._release_events.pop(job_id)

    def _all_jobs_completed(self) -> bool:
        return all(
            job.is_completed
            for job in self.engine.factory.jobs.values()
        )

    def _run(self):
        """Main event-driven scheduling loop."""

        self._schedule_release_events()

        while not self._all_jobs_completed():

            self._cleanup_completed_processes()
            self._cleanup_release_events()

            self._dispatch_available_operations()

            if self._all_jobs_completed():
                break

            self._schedule_release_events()

            waiting_events = [
                process
                for process in self._active_processes.values()
                if not process.processed
            ]

            waiting_events.extend(
                event
                for event in self._release_events.values()
                if not event.processed
            )

            if not waiting_events:
                unfinished_jobs = [
                    job.job_id
                    for job in self.engine.factory.jobs.values()
                    if not job.is_completed
                ]

                raise RuntimeError(
                    "Scheduling deadlock detected. "
                    f"Unfinished jobs: {unfinished_jobs}. "
                    "No active processes or future release events."
                )

            yield self.engine.env.any_of(waiting_events)

    def run(self) -> SimulationEngine:
        """Execute the scheduling simulation until all jobs complete."""

        if self._started:
            raise RuntimeError(
                "SchedulingRunner can only be run once."
            )

        self._started = True

        runner_process = self.engine.env.process(self._run())
        self.engine.env.run(until=runner_process)

        return self.engine