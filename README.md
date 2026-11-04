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

**Current development stage:** Preparation for benchmarking classical scheduling algorithms.

The next objective is to establish a reproducible benchmark framework before implementing the reinforcement learning environment and PPO agent.
