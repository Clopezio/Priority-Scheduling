# This .py is meant to define what a process is in the program.
# All the program will pass around an Object "Process" stored here

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(order=True)
class Process:
    """
    Represents a single process/job in the scheduling simulation.

    Notes:
    - Lower priority number => higher priority.
    - `seq` is an internal tie-breaker for FCFS ordering among same-priority
      processes (it represents the order the process was enqueued/seen).
    """

    priority: int
    arrival_time: int
    seq: int = field(default=0, compare=True)

    pid: str = field(default="", compare=False)
    burst_time: int = field(default=0, compare=False)

    remaining_time: int = field(default=0, compare=False)
    start_time: int | None = field(default=None, compare=False)
    completion_time: int | None = field(default=None, compare=False)

    def __post_init__(self) -> None:
        if self.burst_time <= 0:
            raise ValueError(f"burst_time must be > 0 for pid={self.pid}")
        if self.arrival_time < 0:
            raise ValueError(f"arrival_time must be >= 0 for pid={self.pid}")
        self.remaining_time = self.burst_time


@dataclass
class TimelineSegment:
    start: int
    end: int
    label: str  