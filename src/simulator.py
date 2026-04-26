# This .py runs the main scheduling simulation
from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .process import Process, TimelineSegment


@dataclass
class SimulationConfig:
    preemptive: bool = False
    context_switch_cost: int = 0  # costo del cambio contesto se vuoi aggiungerlo dopo


@dataclass
class SimulationResult:
    processes: List[Process]
    timeline: List[TimelineSegment]
    preemptions: int = 0
    context_switches: int = 0
    total_time: int = 0


def _append_segment(timeline: List[TimelineSegment], start: int, end: int, label: str) -> None:
    # unisce segmenti contigui con la stessa etichetta per evitare tanti pezzi da 1 tick
    if start == end:
        return
    if timeline and timeline[-1].label == label and timeline[-1].end == start:
        timeline[-1].end = end
    else:
        timeline.append(TimelineSegment(start=start, end=end, label=label))


def simulate(processes: List[Process], cfg: SimulationConfig) -> SimulationResult:
    # ordino per gestire facilmente gli arrivi nel tempo
    procs = sorted(processes, key=lambda p: (p.arrival_time, p.priority, p.pid))

    n = len(procs)
    if n == 0:
        return SimulationResult(processes=[], timeline=[], total_time=0)

    # heap di processi pronti ordinata da process priority poi arrival_time poi seq
    ready: List[Process] = []
    timeline: List[TimelineSegment] = []

    now = 0
    i = 0
    seq_counter = 0

    running: Optional[Process] = None
    preemptions = 0
    context_switches = 0

    def enqueue_arrivals(current_time: int) -> None:
        nonlocal i, seq_counter
        while i < n and procs[i].arrival_time <= current_time:
            p = procs[i]
            p.seq = seq_counter  # seq serve come tie break fcfs
            seq_counter += 1
            heapq.heappush(ready, p)
            i += 1

    def dispatch(next_p: Process) -> None:
        nonlocal running, now, context_switches
        if cfg.context_switch_cost > 0:
            _append_segment(timeline, now, now + cfg.context_switch_cost, "CS")
            now += cfg.context_switch_cost
            context_switches += 1

        running = next_p
        if running.start_time is None:
            running.start_time = now  # prima volta che prende la cpu

    now = min(p.arrival_time for p in procs)

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
                    now = next_time
                else:
                    break

        if cfg.preemptive and running is not None and ready:
            top = ready[0]  # peek del migliore senza pop
            if top.priority < running.priority:
                preemptions += 1
                running.seq = seq_counter  # rientra in coda quindi nuovo ordine fcfs
                seq_counter += 1
                heapq.heappush(ready, running)
                dispatch(heapq.heappop(ready))

        if running is not None:
            _append_segment(timeline, now, now + 1, running.pid)
            running.remaining_time -= 1
            now += 1

            if running.remaining_time == 0:
                running.completion_time = now
                running = None
                completed += 1

    return SimulationResult(
        processes=procs,
        timeline=timeline,
        preemptions=preemptions,
        context_switches=context_switches,
        total_time=now,
    )


if __name__ == "__main__":
    import random

    def calc_priority(burst_time: int, cpu_demand: int, urgency: int) -> int:
        # score piu alto vuol dire processo piu importante
        score = (2 * urgency) + (10 - burst_time) - cpu_demand

        # trasformo lo score in fasce di priorita dove 1 e la piu alta
        if score >= 15:
            return 1
        if score >= 10:
            return 2
        if score >= 5:
            return 3
        if score >= 0:
            return 4
        return 5

    random.seed()  # seed randomico per risultati diversi

    processes: list[Process] = []
    for i in range(1, 6):
        burst = random.randint(1, 10)
        cpu_demand = random.randint(1, 10)
        urgency = random.randint(1, 10)
        arrival = random.randint(0, 10)

        prio = calc_priority(burst, cpu_demand, urgency)

        processes.append(
            Process(
                pid=f"P{i}",
                arrival_time=arrival,
                burst_time=burst,
                priority=prio,
            )
        )

        print(
            f"P{i}: arrival={arrival}, burst={burst}, cpu_demand={cpu_demand}, "
            f"urgency={urgency} => priority={prio}"
        )

    print("\n=== Preemptive ===")
    res = simulate(processes, SimulationConfig(preemptive=True))
    for seg in res.timeline:
        print(seg)

    print("\npreemptions:", res.preemptions)