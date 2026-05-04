from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(order=True)
class Process:
    priority: int
    arrival_time: int
    seq: int = field(default=0, compare=True)

    pid: str = field(default="", compare=False)
    burst_time: int = field(default=0, compare=False)

    remaining_time: int = field(default=0, compare=False)
    start_time: int | None = field(default=None, compare=False)
    completion_time: int | None = field(default=None, compare=False)

    cpu_demand: int = field(default=0, compare=False)
    urgency: int = field(default=0, compare=False)

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