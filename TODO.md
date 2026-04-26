# Priority Scheduling Simulator — TODO

## 0) Decide and document assumptions 
- [X] Priority direction: lower number = higher priority OR higher number = higher priority
- [X] Scheduling mode: non preemptive, preemptive, or both
- [X] Tie-breaker when priorities match and how to
- [X] Time model: tick-based 
- [X] Will we include context switch cost?
- [X] Will we include aging to prevent starvation? 

---

## 1) Project structure 
- [X] Create `src/` 
- [X] Add `src/process.py` 
- [X] Add `src/simulator.py` 
- [X] Add `src/metrics.py` 
- [X] Add `src/cli.py` 
- [X] Add `src/plot.py` (Gantt + charts)

---

## 2) Data model
- [X] Define `Process` (dataclass)
  - inputs: `pid`, `arrival_time`, `burst_time`, `base_priority`
  - runtime: `remaining_time`, `start_time`, `completion_time`
- [X] Define `TimelineSegment` (dataclass)
  - `start`, `end`, `label` (PID / IDLE / CS)
- [X] Define `SimulationConfig` (dataclass)
  - `preemptive` (bool)
  - `lower_number_higher_priority` (bool)
  - `context_switch_cost` (int)
  - `aging_enabled` (bool)
  - `aging_interval` (int)
  - `aging_delta` (int)

---

## 3) Core simulation 
- [X] Sort processes by `arrival_time`
- [X] Maintain:
  - `now` (current time)
  - `ready_queue` (priority-based selection + tie-break)
  - `running` (current process or None)
  - `timeline` list
- [X] Handle arrivals
  - [X] At each tick, enqueue all processes with `arrival_time == now`
- [ ] CPU idle behavior
  - [X] If `running` is None and `ready_queue` empty then add `IDLE` segment for 1 tick
- [ ] Dispatch behavior
  - [X] When selecting a new process, set `start_time` if first time running
  - [X] Update response time = `start_time - arrival_time` 
- [X] Run behavior (tick)
  - [X] Decrement `remaining_time` by 1 tick
  - [X] Append PID segment to timeline
- [X] Completion behavior
  - [X] When `remaining_time == 0`, set `completion_time`, mark completed, clear `running`

---

## 4) Preemption
- [X] Each tick (after arrivals), if `preemptive`:
  - [X] If top of ready queue has higher priority than `running`, preempt:
    - [X] push `running` back into ready queue
    - [X] select and dispatch new `running`
    - [X] increment `preemptions` counter

---

## 5) Context switch overhead 
- [X] If `context_switch_cost > 0`:
  - [X] When switching from one PID to another (including from IDLE to PID), insert `CS` segment
  - [X] Increase `now` accordingly
  - [X] increment `context_switches` counter

---

## 6) Aging 
- [X] If `aging_enabled`:
  - [X] Track waiting time for processes in ready queue
  - [X] Every `aging_interval` ticks waiting, adjust effective priority by `aging_delta`
- [ ] Keep it simple:
  - [ ] effective priority only affects ordering, not `base_priority` (or clearly document if you mutate it)

---

## 7) Metrics 
Compute per process:
- [X] `turnaround_time = completion_time - arrival_time`
- [X] `waiting_time = turnaround_time - burst_time`
- [X] `response_time = start_time - arrival_time` (for non-preemptive and preemptive)
Compute overall:
- [X] averages for waiting / turnaround / response
- [X] CPU utilization (optional but good)
  - [X] utilization = (time running PIDs) / (total time including IDLE + CS)
- [X] throughput = completed processes / total time
- [X] report `preemptions` and `context_switches`

---

## 8) Output formatting
- [ ] Print a clear table (PID, arrival, burst, priority, start, completion, wait, turnaround, response)
- [ ] Print summary averages
- [ ] Print timeline in text form (e.g., segments with start/end/label)

---

## 9) Graphs / visualization
- [ ] Gantt chart (from `timeline`)
- [ ] Bar chart: waiting time per PID
- [ ] Compare runs: aging off vs on (show starvation improvement)

---

## 10) Testing 
- [ ] Add 2–4 deterministic test cases with known outcomes
  - [ ] non-preemptive basic
  - [ ] preemptive arrival causing preemption
  - [ ] tie-breaker correctness
  - [ ] aging prevents starvation (if implemented)
- [ ] Ensure results are reproducible (fixed inputs / optional random seed)
