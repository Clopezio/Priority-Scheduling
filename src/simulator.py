from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Dict, List, Optional

from .process import Process, TimelineSegment


@dataclass
class SimulationConfig:
    preemptive: bool = False
    context_switch_cost: int = 0  
    log_events: bool = True       


@dataclass
class SimulationResult:
    processes: List[Process]
    timeline: List[TimelineSegment]
    events_by_time: Dict[int, str]  
    preemptions: int = 0
    context_switches: int = 0
    total_time: int = 0


def _append_segment(timeline: List[TimelineSegment], start: int, end: int, label: str) -> None:
    if start == end:
        return
    if timeline and timeline[-1].label == label and timeline[-1].end == start:
        timeline[-1].end = end
    else:
        timeline.append(TimelineSegment(start=start, end=end, label=label))


def simulate(processes: List[Process], cfg: SimulationConfig) -> SimulationResult:
    procs = sorted(processes, key=lambda p: (p.arrival_time, p.priority, p.pid))

    n = len(procs)
    if n == 0:
        return SimulationResult(processes=[], timeline=[], events_by_time={}, total_time=0)

    ready: List[Process] = []
    timeline: List[TimelineSegment] = []
    events_by_time: Dict[int, List[str]] = {}

    now = 0
    i = 0
    seq_counter = 0

    running: Optional[Process] = None
    preemptions = 0
    context_switches = 0

    def log_at(t: int, msg: str) -> None:
        if not cfg.log_events:
            return
        events_by_time.setdefault(t, []).append(msg)

    def enqueue_arrivals(current_time: int) -> None:
        nonlocal i, seq_counter
        while i < n and procs[i].arrival_time <= current_time:
            p = procs[i]
            p.seq = seq_counter
            seq_counter += 1
            heapq.heappush(ready, p)
            log_at(current_time, f"arrive {p.pid} prio={p.priority} burst={p.burst_time}")
            i += 1

    def dispatch(next_p: Process) -> None:
        nonlocal running, now, context_switches

        if cfg.context_switch_cost > 0:
            _append_segment(timeline, now, now + cfg.context_switch_cost, "CS")
            log_at(now, f"context switch cost={cfg.context_switch_cost}")
            now += cfg.context_switch_cost
            context_switches += 1

        running = next_p
        if running.start_time is None:
            running.start_time = now
            log_at(now, f"start {running.pid}")
        else:
            log_at(now, f"resume {running.pid}")

    now = min(p.arrival_time for p in procs)
    log_at(now, "simulation start")

    completed = 0
    while completed < n:
        enqueue_arrivals(now)

        if running is None:
            if ready:
                dispatch(heapq.heappop(ready))
            else:
                if i < n:
                    next_time = procs[i].arrival_time
                    _append_segment(timeline, now, next_time, "IDLE")
                    log_at(now, f"idle until {next_time}")
                    now = next_time
                else:
                    break

        if cfg.preemptive and running is not None and ready:
            top = ready[0]
            if top.priority < running.priority:
                preemptions += 1
                log_at(now, f"preempt {running.pid} for {top.pid}")

                running.seq = seq_counter
                seq_counter += 1
                heapq.heappush(ready, running)

                dispatch(heapq.heappop(ready))

        if running is not None:
            log_at(now, f"run {running.pid} remaining_before={running.remaining_time}")
            _append_segment(timeline, now, now + 1, running.pid)
            running.remaining_time -= 1
            now += 1

            if running.remaining_time == 0:
                running.completion_time = now
                log_at(now, f"finish {running.pid}")
                running = None
                completed += 1

    log_at(now, f"simulation end total_time={now}")

    flat: Dict[int, str] = {t: " | ".join(msgs) for t, msgs in sorted(events_by_time.items())}

    return SimulationResult(
        processes=procs,
        timeline=timeline,
        events_by_time=flat,
        preemptions=preemptions,
        context_switches=context_switches,
        total_time=now,
    )

if __name__ == "__main__":
    import random

    def calc_priority(burst_time: int, cpu_demand: int, urgency: int) -> int:
        score = (2 * urgency) + (10 - burst_time) - cpu_demand
        if score >= 15:
            return 1
        if score >= 10:
            return 2
        if score >= 5:
            return 3
        if score >= 0:
            return 4
        return 5

    random.seed()

    processes: list[Process] = []
    generated_meta: list[tuple[str, int, int]] = []  

    for idx in range(1, 6):
        burst = random.randint(1, 10)
        cpu_demand = random.randint(1, 10)
        urgency = random.randint(1, 10)
        arrival = random.randint(0, 10)

        prio = calc_priority(burst, cpu_demand, urgency)
        pid = f"P{idx}"

        processes.append(Process(pid=pid, arrival_time=arrival, burst_time=burst, priority=prio))
        generated_meta.append((pid, cpu_demand, urgency))

    print("processes")
    for p in sorted(processes, key=lambda x: x.pid):
        cpu_demand, urgency = next((cd, u) for (pid, cd, u) in generated_meta if pid == p.pid)
        print(
            f"{p.pid} arrival={p.arrival_time} burst={p.burst_time} "
            f"cpu_demand={cpu_demand} urgency={urgency} priority={p.priority}"
        )

    print("\n=== preemptive ===")
    res = simulate(processes, SimulationConfig(preemptive=True, log_events=True))

    print("\nper time timeline log")
    for t in range(min(res.events_by_time.keys(), default=0), res.total_time + 1):
        if t in res.events_by_time:
            print(f"t={t}: {res.events_by_time[t]}")

    print("\ntimeline segments")
    for seg in res.timeline:
        print(seg)

    print("\npreemptions:", res.preemptions)