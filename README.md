# AI-Based Dynamic Factory Production Scheduling

## Research Project

**AI-Based Dynamic Factory Production Scheduling Using Reinforcement Learning: A Simulation-Based Approach with PPO and Classical Dispatching Rules**

## 1. Project Overview

This research project investigates reinforcement learning-based decision-making for dynamic job-shop production scheduling.

The proposed approach aims to use Proximal Policy Optimization (PPO) to make production scheduling decisions under dynamic manufacturing conditions.

The research will evaluate and compare reinforcement learning-based scheduling against classical dispatching rules, including FIFO, SPT, and EDD, under different production scenarios.

A discrete-event factory simulation model is being developed using SimPy to provide a controlled and reproducible environment for scheduling experiments.

## 2. Research Objectives

The main objectives of this research are:

- Develop a discrete-event factory simulation environment.
- Implement classical dispatching rules as baseline scheduling methods.
- Design a Gymnasium-compatible reinforcement learning environment.
- Train a PPO-based scheduling agent.
- Evaluate scheduling performance under different manufacturing conditions.
- Compare reinforcement learning against classical scheduling approaches using quantitative performance metrics.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Main programming language |
| SimPy | Discrete-event simulation |
| Gymnasium | Reinforcement learning environment |
| Stable-Baselines3 | PPO implementation |
| SB3-Contrib | MaskablePPO and action masking |
| PyTorch | Deep learning framework |
| NumPy | Numerical computations |
| Pandas | Experimental data analysis |
| Matplotlib | Result visualization |
| TensorBoard | Training monitoring |
| Pytest | Automated testing |
| Ruff | Code quality and linting |

## 4. Project Architecture

```text
FactorySchedulingAI/
├── agents/          # Reinforcement learning agents and training
├── baselines/       # Classical scheduling algorithms
├── datasets/        # Experimental datasets
├── experiments/     # Benchmarking and experimental analysis
├── factory_sim/     # Factory simulation and domain models
├── logs/            # Training and simulation logs
├── models/          # Trained reinforcement learning models
├── results/         # Experimental results
├── rl_env/          # Gymnasium reinforcement learning environment
├── tests/           # Automated test suite
├── requirements.txt
└── README.md
```

## 5. Implemented Components

### Phase 1: Development Environment and Project Setup

**Status: Completed**

- Python 3.11 development environment configured.
- Virtual environment created.
- Required project dependencies installed.
- Project directory structure established.
- Git repository initialized and configured.
- Testing and linting tools configured.

### Phase 2: Domain Models

**Status: Completed**

Implemented the core domain models:

- `Job`: Represents a production job and its operation sequence.
- `Operation`: Represents an individual production operation, including eligible machines and processing times.
- `Machine`: Represents a production machine and its operational state.
- `MachineStatus`: Defines machine states such as IDLE, BUSY, and DOWN.
- `Factory`: Manages production jobs and machines.

Implemented domain-level validation and lifecycle management:

- Processing time validation.
- Machine eligibility validation.
- Operation sequence management.
- Machine operation lifecycle.
- Machine breakdown and repair state management.
- Duplicate entity validation.

### Phase 3: Factory Simulation Engine

**Status: Completed**

Implemented a discrete-event factory simulation engine using SimPy.

Key features:

- Simulation clock and event management.
- Operation scheduling and execution.
- Sequential multi-operation job execution.
- Job release time constraints.
- Machine availability and reservation management.
- Machine breakdown and repair events.
- Interrupted operation recovery using remaining processing time.
- Event priority handling for simultaneous operation completion and machine breakdown.
- Simulation event logging.
- Validation of invalid and non-finite scheduling times.

### Phase 4: Classical Scheduling Baselines

**Status: Completed**

Implemented three classical dispatching rules:

- **FIFO (First In, First Out):** Prioritizes jobs according to their release times.
- **SPT (Shortest Processing Time):** Prioritizes operations with the shortest processing times.
- **EDD (Earliest Due Date):** Prioritizes jobs with the earliest due dates.

Implemented a scheduling runner to coordinate scheduling decisions and simulation execution.

The runner supports:

- Dispatching available operations.
- Respecting job release times.
- Managing active jobs and machines.
- Sequential operation scheduling.
- Detecting deadlocks and invalid execution states.

### Phase 5: Simulation Performance Metrics

**Status: Completed**

Implemented a separate metrics module for evaluating completed factory simulations.

Currently supported metrics:

- **Makespan:** Completion time of the last job.
- **Mean Flow Time:** Average time jobs spend in the system.
- **Total Tardiness:** Sum of job delays beyond their due dates.
- **Mean Tardiness:** Average tardiness across all jobs.
- **Machine Utilization:** Utilization percentage for each machine.
- **Overall Machine Utilization:** Aggregate machine utilization.
- **Job Completion Times:** Completion time recorded for each job.

The metrics module uses simulation event logs and machine performance counters.

## 6. Testing and Code Quality

**Latest verification: November 4, 2026**

The project currently has **67 automated tests**, all passing.

| Test Module | Tests |
|---|---:|
| Domain Models | 8 |
| Factory | 8 |
| Simulation Engine | 26 |
| Scheduling Runner | 9 |
| Classical Baselines | 11 |
| Performance Metrics | 5 |
| **Total** | **67** |

Quality assurance results:

- Pytest: 67 passed.
- Ruff: All checks passed.
- No failing tests in the latest full test run.

Run the complete test suite:

```bash
python -m pytest -v
```

Run code quality checks:

```bash
ruff check .
```

## 7. Upcoming Development Phases

### Phase 6: Benchmark Infrastructure

- Develop reusable factory production scenarios.
- Execute FIFO, SPT, and EDD on identical scenarios.
- Compare scheduling performance using the implemented metrics.
- Export benchmark results to CSV.
- Analyze the strengths and limitations of classical dispatching rules.

### Phase 7: Reinforcement Learning Environment

- Implement a Gymnasium-compatible environment.
- Define the observation and state representation.
- Design the action space.
- Implement action masking for invalid scheduling decisions.
- Design and validate the reward function.

### Phase 8: PPO Agent and Training

- Implement PPO / MaskablePPO.
- Configure training parameters.
- Train and evaluate scheduling agents.
- Monitor training using TensorBoard.

### Phase 9: Experimental Evaluation

- Compare PPO against classical scheduling baselines.
- Evaluate performance under different workload levels.
- Investigate dynamic job arrivals and machine breakdowns.
- Study processing time uncertainty and sequence-dependent setup times.
- Analyze the impact of different due-date tightness levels.
- Visualize and interpret experimental results.

## 8. Reproducibility

Python dependencies are recorded in `requirements.txt`.

Experiments will use controlled random seeds and documented configuration files to support reproducibility.

All scheduling algorithms will be evaluated using equivalent factory scenarios and consistent performance metrics.

## 9. Current Project Status

The following components have been implemented and tested:

- Domain models and factory management.
- Discrete-event factory simulation engine.
- Machine breakdown and repair handling.
- Classical scheduling algorithms (FIFO, SPT, EDD).
- Scheduling runner.
- Simulation performance metrics.
- Automated test suite.

**Current development stage:** Initial benchmarking of classical scheduling algorithms.

The benchmark infrastructure has been implemented, and the first comparative experiment using seed=42 has been completed.

SPT achieved the best results in makespan, mean flow time, and tardiness metrics in this initial scenario.

The next objective is to evaluate the robustness of these results across multiple random seeds, workload levels, and due-date tightness configurations before proceeding to reinforcement learning.


## 10. Preliminary Baseline Benchmark Results

**Experiment Status: Initial Benchmark Completed**

The first comparative benchmark was successfully conducted using the implemented classical scheduling algorithms.

### Experimental Configuration

| Parameter | Value |
|---|---|
| Random Seed | 42 |
| Scheduling Algorithms | FIFO, SPT, EDD |
| Simulation Environment | SimPy |
| Evaluation | Identical factory scenario |
| Metrics | Makespan, Mean Flow Time, Total Tardiness, Mean Tardiness, Machine Utilization |

### Benchmark Results

| Performance Metric | FIFO | SPT | EDD |
|---|---:|---:|---:|
| Makespan | 87.98 | **76.25** | 82.98 |
| Mean Flow Time | 46.46 | **35.86** | 37.69 |
| Total Tardiness | 227.63 | **121.63** | 141.14 |
| Mean Tardiness | 22.76 | **12.16** | 14.11 |
| Overall Machine Utilization | **89.41%** | 80.00% | 83.96% |

### Initial Performance Analysis

SPT achieved the best results across three major scheduling performance dimensions in this experimental scenario:

- Makespan
- Mean Flow Time
- Total Tardiness

Compared with FIFO, SPT achieved the following improvements:

| Metric | Improvement |
|---|---:|
| Makespan | 13.33% |
| Mean Flow Time | 22.82% |
| Total Tardiness | 46.57% |

These results indicate that SPT was particularly effective at reducing job completion times and delivery delays in the initial scenario.

### Machine Utilization Analysis

FIFO achieved the highest overall machine utilization (89.41%), followed by EDD (83.96%) and SPT (80.00%).

However, higher machine utilization does not necessarily indicate better overall scheduling performance.

In this experiment, SPT achieved a shorter makespan and lower flow time and tardiness despite its lower aggregate utilization. Therefore, machine utilization should be interpreted together with other performance metrics.

### Research Interpretation and Limitations

The initial experiment provides preliminary evidence that SPT can outperform FIFO and EDD under the evaluated factory scenario.

However, these findings must not be interpreted as evidence of general algorithmic superiority.

The experiment was conducted using a single random seed (seed=42). Further experiments are required to evaluate whether the observed performance differences remain consistent under different conditions.

The next experimental steps are:

- Evaluate multiple random seeds.
- Investigate different production workload levels.
- Examine different due-date tightness configurations.
- Analyze the consistency and variability of scheduling performance.
- Compare the classical baselines under dynamic manufacturing conditions.

These experiments will establish a stronger baseline for the subsequent evaluation of the PPO-based reinforcement learning scheduling agent.
