# Priority Scheduling (Preemptive + Non-preemptive)

A small Python simulator for **Priority CPU Scheduling** supporting both:

- **Non-preemptive priority scheduling**: once a process starts, it runs until it finishes.
- **Preemptive priority scheduling**: a newly-arrived higher-priority process can interrupt the currently running process.

**Priority rule:** lower number = higher priority (e.g., priority `1` runs before `2`).

**Tie-breaker:** FCFS (first-come, first-served) for equal priority.


## Project Structure

```text
Priority-Scheduling/
  src/
    __init__.py
    process.py
    simulator.py
```

- `src/process.py` defines the `Process` and `TimelineSegment` data models.
- `src/simulator.py` contains the `simulate(...)` function and simulation config/result types.

## Requirements

- Python 3.10+ 

## How to Run

Download the project from this github reposiotory.

Open the project, and then open a terminal in the root folder.

navigate to 

```bash
cd src
```

execute: 

```bash
python -m src.simulator
```

> Note: using `-m` matters because `src/simulator.py` uses relative imports (e.g., `from .process import Process`).


## Input Model

Each process has:
- `pid`: process id (string)
- `arrival_time`: when the process becomes ready (int time units)
- `burst_time`: CPU time needed (int time units)
- `priority`: smaller value means higher priority

Example:
```python
Process(pid="P2", arrival_time=1, burst_time=4, priority=1)
```


## Output

The simulator returns a `SimulationResult`:
- `TimelineSegment(start, end, label)`
- `label` is usually a PID like `"P1"` or `"IDLE"` (or `"CS"` if context switching cost is enabled)

Example segment meaning:
- `TimelineSegment(start=1, end=5, label='P2')` means **P2 ran from time 1 up to (not including) time 5**.
