"""
SatQuery AI — Execution Trace Builder
Tracks each pipeline stage with timing, status, and details.
"""

import time
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class TraceEntry:
    stage: str
    status: str  # "ok" | "failed" | "skipped"
    duration_ms: int
    detail: str


class TraceBuilder:
    """Builds an execution trace as the request flows through the pipeline."""

    def __init__(self):
        self._entries: List[TraceEntry] = []
        self._current_stage: Optional[str] = None
        self._stage_start: Optional[float] = None

    def start_stage(self, stage: str):
        """Mark the beginning of a pipeline stage."""
        self._current_stage = stage
        self._stage_start = time.time()

    def end_stage(self, status: str = "ok", detail: str = ""):
        """Mark the end of the current pipeline stage."""
        if self._current_stage is None or self._stage_start is None:
            return

        duration_ms = int((time.time() - self._stage_start) * 1000)
        self._entries.append(TraceEntry(
            stage=self._current_stage,
            status=status,
            duration_ms=duration_ms,
            detail=detail
        ))
        self._current_stage = None
        self._stage_start = None

    def add_completed_stage(self, stage: str, status: str, duration_ms: int, detail: str = ""):
        """Add a stage that's already been measured."""
        self._entries.append(TraceEntry(
            stage=stage,
            status=status,
            duration_ms=duration_ms,
            detail=detail
        ))

    def get_trace(self) -> List[Dict]:
        """Return the full trace as a list of dicts."""
        return [asdict(entry) for entry in self._entries]

    def get_total_duration_ms(self) -> int:
        """Return the total duration of all stages."""
        return sum(entry.duration_ms for entry in self._entries)
