# Priority Scheduling Simulator — TODO

## 0) Decide and document assumptions 
- [ ] Priority direction: lower number = higher priority OR higher number = higher priority
- [ ] Scheduling mode: non preemptive, preemptive, or both
- [ ] Tie-breaker when priorities match and how to
- [ ] Time model: tick-based 
- [ ] Will we include context switch cost?
- [ ] Will we include aging to prevent starvation? 

---

## 1) Project structure 
- [ ] Create `src/` 
- [ ] Add `src/process.py` 
- [ ] Add `src/simulator.py` 
- [ ] Add `src/metrics.py` 
- [ ] Add `src/cli.py` 
- [ ] Add `src/plot.py` (Gantt + charts)

---

## 2) Data model
- [ ] Define `Process` (dataclass)
  - inputs: `pid`, `arrival_time`, `burst_time`, `base_priority`
  - runtime: `remaining_time`, `start_time`, `completion_time`
- [ ] Define `TimelineSegment` (dataclass)
  - `start`, `end`, `label` (PID / IDLE / CS)
- [ ] Define `SimulationConfig` (dataclass)
  - `preemptive` (bool)
  - `lower_number_higher_priority` (bool)
  - `context_switch_cost` (int)
  - `aging_enabled` (bool)
  - `aging_interval` (int)
  - `aging_delta` (int)

---

## 3) Core simulation 
- [ ] Sort processes by `arrival_time`
- [ ] Maintain:
  - `now` (current time)
  - `ready_queue` (priority-based selection + tie-break)
  - `running` (current process or None)
  - `timeline` list
- [ ] Handle arrivals
  - [ ] At each tick, enqueue all processes with `arrival_time == now`
- [ ] CPU idle behavior
  - [ ] If `running` is None and `ready_queue` empty then add `IDLE` segment for 1 tick
- [ ] Dispatch behavior
  - [ ] When selecting a new process, set `start_time` if first time running
  - [ ] Update response time = `start_time - arrival_time` 
- [ ] Run behavior (tick)
  - [ ] Decrement `remaining_time` by 1 tick
  - [ ] Append PID segment to timeline
- [ ] Completion behavior
  - [ ] When `remaining_time == 0`, set `completion_time`, mark completed, clear `running`

---

## 4) Preemption
- [ ] Each tick (after arrivals), if `preemptive`:
  - [ ] If top of ready queue has higher priority than `running`, preempt:
    - [ ] push `running` back into ready queue
    - [ ] select and dispatch new `running`
    - [ ] increment `preemptions` counter

---

## 5) Context switch overhead 
- [ ] If `context_switch_cost > 0`:
  - [ ] When switching from one PID to another (including from IDLE to PID), insert `CS` segment
  - [ ] Increase `now` accordingly
  - [ ] increment `context_switches` counter

---

## 6) Aging 
- [ ] If `aging_enabled`:
  - [ ] Track waiting time for processes in ready queue
  - [ ] Every `aging_interval` ticks waiting, adjust effective priority by `aging_delta`
- [ ] Keep it simple:
  - [ ] effective priority only affects ordering, not `base_priority` (or clearly document if you mutate it)

---

## 7) Metrics 
Compute per process:
- [ ] `turnaround_time = completion_time - arrival_time`
- [ ] `waiting_time = turnaround_time - burst_time`
- [ ] `response_time = start_time - arrival_time` (for non-preemptive and preemptive)
Compute overall:
- [ ] averages for waiting / turnaround / response
- [ ] CPU utilization (optional but good)
  - [ ] utilization = (time running PIDs) / (total time including IDLE + CS)
- [ ] throughput = completed processes / total time
- [ ] report `preemptions` and `context_switches`

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
