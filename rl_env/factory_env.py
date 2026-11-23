from dataclasses import asdict, replace
from typing import ClassVar

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from experiments.scenarios import ScenarioConfig, build_factory
from factory_sim.enums import MachineStatus
from factory_sim.metrics import SimulationMetrics
from factory_sim.simulation import SimulationEngine


class FactorySchedulingEnv(gym.Env):
    """
    Gymnasium environment for dynamic factory scheduling.

    Each action assigns the current operation of one job
    to one available and eligible machine.
    """

    metadata: ClassVar[dict] = {"render_modes": []}

    def __init__(
        self,
        config: ScenarioConfig | None = None,
    ):
        super().__init__()

        self.config = config or ScenarioConfig()

        self.job_ids = [
            f"J{i + 1}"
            for i in range(self.config.job_count)
        ]

        self.machine_ids = [
            f"M{i + 1}"
            for i in range(self.config.machine_count)
        ]

        self.job_count = self.config.job_count
        self.machine_count = self.config.machine_count

        self.max_processing_time = float(
            self.config.max_processing_time
        )

        serial_horizon = (
            self.config.max_release_time
            + self.job_count
            * self.config.max_operations
            * self.max_processing_time
        )

        due_date_horizon = (
            self.config.max_release_time
            + self.config.max_operations
            * self.max_processing_time
            * self.config.due_date_factor
        )

        self.time_scale = max(
            1.0,
            serial_horizon,
            due_date_horizon,
        )

        # One action represents one job-machine assignment.
        self.action_space = spaces.Discrete(
            self.job_count * self.machine_count
        )

        # Per job:
        # released, completed, active, progress,
        # remaining release time, due date,
        # processing time on each machine.
        job_features = 6 + self.machine_count

        # Per machine:
        # four status flags, busy time, current job index.
        machine_features = 6

        observation_size = (
            self.job_count * job_features
            + self.machine_count * machine_features
            + 1
        )

        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(observation_size,),
            dtype=np.float32,
        )

        self.engine: SimulationEngine | None = None

        self._active_jobs: set[str] = set()
        self._active_machines: set[str] = set()

        self._active_processes = {}
        self._job_machine: dict[str, str] = {}

        self._episode_done = False
        self._deadlocked = False

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        episode_config = self.config

        if seed is not None:
            episode_config = replace(
                self.config,
                seed=seed,
            )

        factory = build_factory(episode_config)

        self.engine = SimulationEngine(factory)

        self._active_jobs = set()
        self._active_machines = set()

        self._active_processes = {}
        self._job_machine = {}

        self._episode_done = False
        self._deadlocked = False

        self._advance_until_decision()

        observation = self._get_observation()

        info = {
            "current_time": self.engine.current_time,
            "action_mask": self.action_masks(),
        }

        return observation, info

    def step(self, action):
        if self.engine is None:
            raise RuntimeError(
                "Environment must be reset before calling step()."
            )

        if self._episode_done:
            raise RuntimeError(
                "Episode has ended. Call reset() before step()."
            )

        action = int(action)

        if not self.action_space.contains(action):
            raise ValueError(
                f"Action {action} is outside the action space."
            )

        mask = self.action_masks()

        # MaskablePPO should never select an invalid action.
        # This fallback also keeps ordinary Gymnasium checking safe.
        if not mask[action]:
            return (
                self._get_observation(),
                -1.0,
                False,
                False,
                {
                    "invalid_action": True,
                    "current_time": self.engine.current_time,
                    "action_mask": mask,
                },
            )

        previous_time = self.engine.current_time

        self._completed_jobs_before = {
            job_id
            for job_id in self.job_ids
            if self.engine.factory.get_job(job_id).is_completed
        }

        job_index, machine_index = divmod(
            action,
            self.machine_count,
        )

        job_id = self.job_ids[job_index]
        machine_id = self.machine_ids[machine_index]

        process = self.engine.schedule_operation(
            job_id,
            machine_id,
        )

        self._active_jobs.add(job_id)
        self._active_machines.add(machine_id)

        self._active_processes[job_id] = process
        self._job_machine[job_id] = machine_id

        self._advance_until_decision()

        elapsed_time = (
            self.engine.current_time - previous_time
        )

        newly_completed = [
            job_id
            for job_id in self.job_ids
            if (
                self.engine.factory.get_job(job_id).is_completed
                and job_id not in self._completed_jobs_before
            )
        ]

        tardiness = sum(
            self._get_job_tardiness(job_id)
            for job_id in newly_completed
        )

        reward = -(
            elapsed_time + tardiness
        ) / self.time_scale

        terminated = self._all_jobs_completed()
        truncated = self._deadlocked and not terminated

        self._episode_done = terminated or truncated

        info = {
            "current_time": self.engine.current_time,
            "elapsed_time": elapsed_time,
            "newly_completed_jobs": newly_completed,
            "tardiness": tardiness,
            "action_mask": self.action_masks(),
        }

        if terminated:
            metrics = SimulationMetrics.calculate(
                self.engine
            )

            info["metrics"] = asdict(metrics)

        if truncated:
            info["termination_reason"] = "deadlock"

        return (
            self._get_observation(),
            float(reward),
            terminated,
            truncated,
            info,
        )

    def action_masks(self) -> np.ndarray:
        """
        Return a boolean mask for valid job-machine assignments.

        Required by sb3-contrib MaskablePPO.
        """

        mask = np.zeros(
            self.action_space.n,
            dtype=bool,
        )

        if self.engine is None or self._episode_done:
            return mask

        current_time = self.engine.current_time

        for job_index, job_id in enumerate(self.job_ids):
            job = self.engine.factory.get_job(job_id)

            if job.is_completed:
                continue

            if job_id in self._active_jobs:
                continue

            if current_time < job.release_time:
                continue

            operation = job.current_operation

            if operation is None:
                continue

            for machine_index, machine_id in enumerate(
                self.machine_ids
            ):
                machine = self.engine.factory.get_machine(
                    machine_id
                )

                if not machine.is_available:
                    continue

                if machine_id in self._active_machines:
                    continue

                if machine_id not in operation.eligible_machines:
                    continue

                action = (
                    job_index * self.machine_count
                    + machine_index
                )

                mask[action] = True

        return mask

    def _advance_until_decision(self):
        """
        Advance SimPy until:
        - At least one valid action becomes available,
        - All jobs are completed,
        - Or the simulation reaches a deadlock.
        """

        if self.engine is None:
            raise RuntimeError("Simulation engine is not initialized.")

        simpy_env = self.engine.env

        while True:
            self._cleanup_finished_processes()

            if self._all_jobs_completed():
                return

            if self.action_masks().any():
                return

            current_time = self.engine.current_time

            future_releases = [
                self.engine.factory.get_job(job_id).release_time
                for job_id in self.job_ids
                if (
                    not self.engine.factory.get_job(job_id).is_completed
                    and job_id not in self._active_jobs
                    and self.engine.factory.get_job(job_id).release_time
                    > current_time
                )
            ]

            next_release = (
                min(future_releases)
                if future_releases
                else None
            )

            next_event = simpy_env.peek()

            # No scheduled SimPy event: wait for the next job release.
            if next_event == float("inf"):
                if next_release is None:
                    self._deadlocked = True
                    return

                simpy_env.timeout(
                    next_release - current_time
                )

            # A job will be released before the next SimPy event.
            elif (
                next_release is not None
                and next_release < next_event
            ):
                simpy_env.timeout(
                    next_release - current_time
                )

            simpy_env.step()

            # Process all events scheduled at the same simulation time.
            while simpy_env.peek() <= self.engine.current_time:
                simpy_env.step()

            self._cleanup_finished_processes()

    def _cleanup_finished_processes(self):
        for job_id, process in list(
            self._active_processes.items()
        ):
            if not process.processed:
                continue

            machine_id = self._job_machine.pop(job_id)

            self._active_jobs.discard(job_id)
            self._active_machines.discard(machine_id)

            del self._active_processes[job_id]

    def _all_jobs_completed(self) -> bool:
        if self.engine is None:
            return False

        return all(
            self.engine.factory.get_job(job_id).is_completed
            for job_id in self.job_ids
        )

    def _get_job_tardiness(self, job_id: str) -> float:
        job = self.engine.factory.get_job(job_id)

        completion_event = next(
            (
                event
                for event in reversed(self.engine.event_log)
                if (
                    event["event"] == "operation_completed"
                    and event["job_id"] == job_id
                    and event["operation_id"]
                    == job.operations[-1].operation_id
                )
            ),
            None,
        )

        if completion_event is None:
            return 0.0

        return max(
            0.0,
            completion_event["time"] - job.due_date,
        )

    def _get_observation(self) -> np.ndarray:
        if self.engine is None:
            raise RuntimeError("Environment is not initialized.")

        current_time = self.engine.current_time

        features = []

        for job_id in self.job_ids:
            job = self.engine.factory.get_job(job_id)

            released = current_time >= job.release_time
            completed = job.is_completed
            active = job_id in self._active_jobs

            progress = (
                job.current_operation_index / len(job.operations)
            )

            remaining_release = max(
                0.0,
                job.release_time - current_time,
            )

            features.extend(
                [
                    float(released),
                    float(completed),
                    float(active),
                    progress,
                    remaining_release / self.time_scale,
                    job.due_date / self.time_scale,
                ]
            )

            operation = job.current_operation

            for machine_id in self.machine_ids:
                if (
                    operation is not None
                    and machine_id in operation.eligible_machines
                ):
                    processing_time = (
                        operation.get_processing_time(machine_id)
                    )

                    normalized_time = (
                        processing_time / self.max_processing_time
                    )
                else:
                    normalized_time = 0.0

                features.append(normalized_time)

        status_mapping = {
            MachineStatus.IDLE: 0,
            MachineStatus.BUSY: 1,
            MachineStatus.DOWN: 2,
            MachineStatus.SETUP: 3,
        }

        for machine_index, machine_id in enumerate(
            self.machine_ids
        ):
            machine = self.engine.factory.get_machine(
                machine_id
            )

            status_features = [0.0] * 4
            status_features[
                status_mapping[machine.status]
            ] = 1.0

            features.extend(status_features)

            normalized_busy_time = min(
                1.0,
                machine.total_busy_time / self.time_scale,
            )

            features.append(normalized_busy_time)

            current_job_index = 0.0

            if machine.current_job_id in self.job_ids:
                current_job_index = (
                    self.job_ids.index(machine.current_job_id)
                    / max(1, self.job_count - 1)
                )

            features.append(current_job_index)

        features.append(
            min(1.0, current_time / self.time_scale)
        )

        return np.asarray(
            features,
            dtype=np.float32,
        )
