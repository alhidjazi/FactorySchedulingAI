# AI-Based Dynamic Factory Production Scheduling

## Research Project

**AI-Based Dynamic Factory Production Scheduling Using Reinforcement Learning: A Simulation-Based Approach with PPO and Classical Dispatching Rules**

---

## 1. Project Overview

This research project investigates reinforcement learning-based decision-making for dynamic job-shop production scheduling.

The proposed approach aims to use Proximal Policy Optimization (PPO) to make production scheduling decisions under dynamic manufacturing conditions.

The research evaluates reinforcement learning-based scheduling against classical dispatching rules, including FIFO, SPT, and EDD, under different production scenarios.

A discrete-event factory simulation model is being developed using SimPy to provide a controlled and reproducible environment for scheduling experiments.

The research focuses on the following manufacturing challenges:

- Dynamic job arrivals.
- Machine breakdowns and repair operations.
- Processing time uncertainty.
- Sequence-dependent setup times.
- Different production workload levels.
- Different due-date tightness configurations.

## 2. Research Objectives

The main objectives of this research are:

- Develop a discrete-event factory simulation environment.
- Implement classical dispatching rules as baseline scheduling methods.
- Design a Gymnasium-compatible reinforcement learning environment.
- Train a PPO-based scheduling agent.
- Evaluate scheduling performance under different manufacturing conditions.
- Compare reinforcement learning against classical scheduling approaches using quantitative performance metrics.
- Investigate the robustness and statistical significance of scheduling performance differences.

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
| SciPy | Statistical analysis |
| TensorBoard | Training monitoring |
| Pytest | Automated testing |
| Ruff | Code quality and linting |

## 4. Project Architecture

```text
FactorySchedulingAI/
├── agents/          # Reinforcement learning agents and training
├── baselines/       # Classical scheduling algorithms
├── configs/         # Experimental configuration files
├── datasets/        # Experimental datasets
├── experiments/     # Benchmarking and experimental analysis
│   ├── analyze_results.py
│   ├── statistical_tests.py
│   └── plot_results.py
├── factory_sim/     # Factory simulation and domain models
├── logs/            # Training and simulation logs
├── models/          # Trained reinforcement learning models
├── results/
│   └── figures/     # Experimental visualization outputs
├── rl_env/          # Gymnasium reinforcement learning environment
├── tests/           # Automated test suite
├── run_benchmarks.py
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

### Phase 6: Benchmark Infrastructure and Baseline Evaluation

**Status: Implemented — Multi-Seed Experiments Completed**

Developed a reusable benchmark infrastructure for comparing classical scheduling algorithms under identical factory scenarios.

Implemented features:

- Reusable factory production scenarios.
- Reproducible experiments using controlled random seeds.
- Execution of FIFO, SPT, and EDD on identical scenarios.
- Automated performance metric collection.
- Benchmark result export to CSV.
- Multi-scenario experimental execution.
- Statistical summary generation.
- Statistical comparison infrastructure.
- Performance visualization.

Three benchmark scenarios have been evaluated:

| Scenario | Production Jobs | Machines |
|---|---:|---:|
| Baseline 10x3 | 10 | 3 |
| Baseline 25x3 | 25 | 3 |
| Baseline 50x3 | 50 | 3 |

Each scheduler/scenario combination was evaluated using 30 random seeds.

**Experimental configuration:**

| Parameter | Value |
|---|---:|
| Scenarios | 3 |
| Scheduling Algorithms | 3 |
| Experiments per Combination | 30 |
| Total Experiments | 270 |
| Random Seeds | 30 per combination |
| Simulation Framework | SimPy |

The benchmark infrastructure produces the following experimental outputs:

- `results/`: Raw and aggregated experimental results.
- `results/statistical_summary.csv`: Statistical summaries of benchmark performance.
- `results/statistical_tests.csv`: Statistical comparison results.
- `results/figures/`: Performance visualization outputs.

### Phase 7: Statistical Analysis and Visualization

**Status: Implemented — Final Statistical Interpretation in Progress**

Implemented an experimental analysis workflow to evaluate the performance of classical scheduling algorithms.

The analysis covers:

- Makespan comparison.
- Mean flow time comparison.
- Total tardiness comparison.
- Mean performance evaluation.
- Standard deviation analysis.
- Statistical comparison of scheduling algorithms.
- Visualization of experimental results.

Three performance comparison figures have been generated:

1. `makespan_comparison.png`
2. `mean_flow_time_comparison.png`
3. `total_tardiness_comparison.png`

The visualization script is located at:

```text
experiments/plot_results.py
```

The updated visualization implementation calculates two-sided 95% Student's t confidence intervals using the experiment count and sample standard deviation.

The following statistical concepts are considered in the analysis:

- Mean and standard deviation.
- Standard error.
- 95% confidence intervals.
- Statistical significance.
- Effect size.
- Paired statistical comparisons where experimental pairing is appropriate.

The statistical analysis will be used to determine whether observed performance differences are statistically significant rather than relying solely on differences in average values.

**Note:** Statistical significance and final interpretation of the multi-seed results remain subject to verification.

## 6. Testing and Code Quality

**Latest verification: November 19, 2026**

The project currently has **76 automated tests**, all passing.

Latest test execution:

```text
76 passed
```

Quality assurance:

- Pytest: 76 passed.
- Ruff: Import-order issues identified in two analysis scripts; automatic correction is pending.
- No failing tests in the latest full test run.

Run the complete test suite:

```bash
python -m pytest -v
```

Run code quality checks:

```bash
ruff check .
```

Run tests in quiet mode:

```bash
python -m pytest -q
```

## 7. Upcoming Development Phases

### Phase 8: Reinforcement Learning Environment

**Status: Planned**

- Implement a Gymnasium-compatible environment.
- Define the observation and state representation.
- Design the action space.
- Implement action masking for invalid scheduling decisions.
- Design and validate the reward function.
- Integrate the environment with the existing factory simulation engine.

### Phase 9: PPO Agent and Training

**Status: Planned**

- Implement PPO / MaskablePPO.
- Configure training parameters.
- Train and evaluate scheduling agents.
- Monitor training using TensorBoard.
- Investigate training stability and convergence.
- Evaluate the trained policy on unseen random seeds.

### Phase 10: Experimental Evaluation

**Status: Planned**

- Compare PPO against classical scheduling baselines.
- Evaluate performance under different workload levels.
- Investigate dynamic job arrivals and machine breakdowns.
- Study processing time uncertainty and sequence-dependent setup times.
- Analyze the impact of different due-date tightness levels.
- Evaluate generalization across different factory scenarios.
- Analyze statistical significance and effect sizes.
- Visualize and interpret experimental results.

## 8. Reproducibility

Python dependencies are recorded in `requirements.txt`.

Experiments use controlled random seeds and documented configuration files to support reproducibility.

All scheduling algorithms are evaluated using equivalent factory scenarios and consistent performance metrics.

The benchmark infrastructure is designed to support repeated experiments and quantitative comparisons across different production conditions.

## 9. Current Project Status

The following components have been implemented and tested:

- Domain models and factory management.
- Discrete-event factory simulation engine.
- Machine breakdown and repair handling.
- Classical scheduling algorithms (FIFO, SPT, EDD).
- Scheduling runner.
- Simulation performance metrics.
- Reusable benchmark infrastructure.
- Three production benchmark scenarios.
- Multi-seed experimental execution.
- Statistical summary generation.
- Statistical comparison infrastructure.
- Performance visualization.
- Automated test suite.

**Current development stage: Multi-Seed Baseline Evaluation and Statistical Analysis.**

The benchmark infrastructure has been implemented and evaluated across three production scenarios using 30 random seeds for each scheduler/scenario combination.

A total of 270 baseline experiments have been conducted.

Performance visualization has been generated for makespan, mean flow time, and total tardiness.

The current experimental analysis focuses on determining the consistency and statistical significance of the observed performance differences.

The next major development objective is to implement the Gymnasium-compatible reinforcement learning environment and integrate the PPO-based scheduling agent.

## 10. Preliminary Baseline Benchmark Results

**Experiment Status: Initial Single-Seed Benchmark Completed**

The first comparative benchmark was conducted using the implemented classical scheduling algorithms.

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

- Makespan.
- Mean Flow Time.
- Total Tardiness.

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

In this experiment, SPT achieved a shorter makespan and lower flow time and tardiness despite its lower aggregate utilization.

Therefore, machine utilization should be interpreted together with other performance metrics.

### Research Interpretation and Limitations

The initial experiment provides preliminary evidence that SPT can outperform FIFO and EDD under the evaluated factory scenario.

However, these findings must not be interpreted as evidence of general algorithmic superiority.

The experiment was conducted using a single random seed (seed=42). Further experiments are required to evaluate whether the observed performance differences remain consistent under different conditions.

The subsequent multi-seed benchmark experiments expand the evaluation to three production scenarios and 30 random seeds per scheduler/scenario combination.

The statistical analysis is intended to establish whether the initial observations remain consistent across repeated experiments.

These experiments will establish a stronger and more reproducible baseline for the subsequent evaluation of the PPO-based reinforcement learning scheduling agent.

---

**Research Project:** AI-Based Dynamic Factory Production Scheduling Using Reinforcement Learning

**Current Milestone:** Multi-Seed Classical Baseline Evaluation

**Next Milestone:** Gymnasium Environment and PPO Integration