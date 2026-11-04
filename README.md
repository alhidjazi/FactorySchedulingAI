# AI-Based Dynamic Factory Production Scheduling

## Research Project

**AI-Based Dynamic Factory Production Scheduling Using Reinforcement Learning: A Simulation-Based Approach with PPO and Classical Dispatching Rules**

## Research Objective

This project investigates reinforcement learning-based decision-making for dynamic job-shop production scheduling.

The proposed system uses Proximal Policy Optimization (PPO) to make production scheduling decisions under dynamic manufacturing conditions.

The research aims to compare reinforcement learning-based scheduling against classical dispatching rules under different production scenarios.

## Technology Stack

- Python 3.11
- SimPy
- Gymnasium
- Stable-Baselines3
- SB3-Contrib (MaskablePPO)
- NumPy
- Pandas
- Matplotlib
- TensorBoard

## Scheduling Algorithms

- PPO / MaskablePPO
- FIFO (First In, First Out)
- EDD (Earliest Due Date)
- SPT (Shortest Processing Time)

## Research Scenarios

- Dynamic job arrivals
- Machine breakdowns
- Processing time uncertainty
- Sequence-dependent setup times
- Different workload levels
- Different due-date tightness levels

## Evaluation Metrics

- Mean tardiness
- Total tardiness
- Makespan
- Average flow time
- Machine utilization
- On-time delivery rate

## Project Architecture

```text
FactorySchedulingAI/
├── agents/          # PPO agent and training
├── baselines/       # Classical scheduling algorithms
├── datasets/        # Experimental datasets
├── experiments/     # Benchmarking and ablation studies
├── factory_sim/     # Discrete-event factory simulation
├── logs/            # Training logs
├── models/          # Trained models
├── results/         # Experimental results
├── rl_env/          # Reinforcement learning environment
├── tests/           # Automated tests
├── requirements.txt
└── README.md
```

## Development Progress

### Phase 1: Development Environment and Project Setup

**Status: Completed**

- Python 3.11 development environment configured.
- Virtual environment created.
- Required project dependencies installed.
- Project directory structure established.
- Git repository initialized and configured.

### Phase 2: Domain Models

**Status: Completed**

Implemented the core domain models:

- `Job`: Represents a production job and its operation sequence.
- `Operation`: Represents an individual production operation.
- `Machine`: Represents a production machine and its operational state.
- `MachineStatus`: Defines machine states.

Implemented domain-level validation and lifecycle management:

- Processing time validation.
- Machine eligibility validation.
- Operation sequence management.
- Machine operation lifecycle.
- Machine breakdown and repair state management.

### Phase 3: Factory Simulation Engine

**Status: Completed**

Implemented a discrete-event factory simulation environment using SimPy.

Key features:

- `Factory` class for managing production jobs and machines.
- Simulation clock and event management.
- Operation scheduling and execution.
- Multi-operation job execution.
- Job release time constraints.
- Machine availability and busy-state management.
- Machine breakdown and repair events.
- Interrupted operation recovery using remaining processing time.
- Event priority handling for simultaneous operation completion and machine breakdown.
- Simulation event logging.
- Validation of invalid and non-finite scheduling times.

### Quality Assurance

Latest verification: November 4, 2026.

- Ruff linting: Passed.
- Automated tests: 42 passed.
- Domain model tests: Passed.
- Factory management tests: Passed.
- Simulation engine tests: Passed.

## Upcoming Development Phases

### Phase 4: Classical Scheduling Baselines

- FIFO (First In, First Out)
- SPT (Shortest Processing Time)
- EDD (Earliest Due Date)

### Phase 5: Reinforcement Learning Environment

- Gymnasium environment implementation.
- State and observation design.
- Action space definition.
- Action masking for invalid scheduling decisions.
- Reward function design.

### Phase 6: PPO Agent and Training

- PPO / MaskablePPO implementation.
- Training configuration.
- Model evaluation.
- TensorBoard monitoring.

### Phase 7: Experimental Evaluation

- Comparison of PPO against classical baselines.
- Dynamic production scenarios.
- Performance evaluation using defined metrics.
- Experimental analysis and visualization.

## Reproducibility

Python dependencies are recorded in `requirements.txt`.

Experiments will use controlled random seeds and documented configuration files to support reproducibility.

## Project Status

The domain modeling and discrete-event factory simulation engine have been implemented and validated.

The next development stage is the implementation of classical scheduling baselines.
