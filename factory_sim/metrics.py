from dataclasses import dataclass

from factory_sim.simulation import SimulationEngine


@dataclass(frozen=True)
class SimulationMetrics:
    """Performance metrics for a completed factory simulation."""

    makespan: float
    mean_flow_time: float
    total_tardiness: float
    mean_tardiness: float
    machine_utilization: dict[str, float]
    overall_machine_utilization: float
    completion_times: dict[str, float]

    @classmethod
    def calculate(
        cls,
        engine: SimulationEngine,
    ) -> "SimulationMetrics":
        factory = engine.factory

        if not factory.jobs:
            raise ValueError(
                "Cannot calculate metrics without jobs."
            )

        if not factory.machines:
            raise ValueError(
                "Cannot calculate metrics without machines."
            )

        unfinished_jobs = [
            job.job_id
            for job in factory.jobs.values()
            if not job.is_completed
        ]

        if unfinished_jobs:
            raise RuntimeError(
                "Cannot calculate metrics before all jobs complete. "
                f"Unfinished jobs: {unfinished_jobs}"
            )

        completion_times: dict[str, float] = {}


        for event in engine.event_log:
            if event["event"] != "operation_completed":
                continue

            job_id = str(event["job_id"])

            if job_id not in factory.jobs:
                raise RuntimeError(
                    f"Unknown job in completion event: {job_id}"
                )

            job = factory.jobs[job_id]

            final_operation_id = job.operations[-1].operation_id

            if str(event["operation_id"]) != final_operation_id:
                continue

            completion_time = float(event["time"])

            if job_id in completion_times:
                raise RuntimeError(
                    f"Duplicate completion event for job {job_id}."
                )

            completion_times[job_id] = completion_time


        missing_jobs = (
            set(factory.jobs) - set(completion_times)
        )

        if missing_jobs:
            raise RuntimeError(
                "Missing completion events for jobs: "
                f"{sorted(missing_jobs)}"
            )

        makespan = max(completion_times.values())

        flow_times = {
            job_id: completion_times[job_id]
            - job.release_time
            for job_id, job in factory.jobs.items()
        }

        tardiness_values = {
            job_id: max(
                0.0,
                completion_times[job_id] - job.due_date,
            )
            for job_id, job in factory.jobs.items()
        }

        mean_flow_time = (
            sum(flow_times.values()) / len(flow_times)
        )

        total_tardiness = sum(tardiness_values.values())

        mean_tardiness = (
            total_tardiness / len(tardiness_values)
        )

        if makespan <= 0:
            raise RuntimeError(
                "Makespan must be positive."
            )

        machine_utilization = {
            machine.machine_id: (
                machine.total_busy_time / makespan
            ) * 100.0
            for machine in factory.machines.values()
        }

        total_busy_time = sum(
            machine.total_busy_time
            for machine in factory.machines.values()
        )

        overall_machine_utilization = (
            total_busy_time
            / (makespan * factory.machine_count)
        ) * 100.0

        return cls(
            makespan=makespan,
            mean_flow_time=mean_flow_time,
            total_tardiness=total_tardiness,
            mean_tardiness=mean_tardiness,
            machine_utilization=machine_utilization,
            overall_machine_utilization=(
                overall_machine_utilization
            ),
            completion_times=completion_times,
        )
