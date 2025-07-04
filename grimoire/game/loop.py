from __future__ import annotations

"""Simple game loop & event scheduling system.

This implementation keeps dependencies minimal – it uses `threading.Timer` for
real-time loops but can also operate in manual *turn-based* mode where each tick
is triggered explicitly."""

import time
import threading
from typing import Callable, List, Tuple, Any, Optional

# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Priority queue of (timestamp, callable, args, kwargs)."""

    def __init__(self):
        self._events: List[Tuple[float, Callable, tuple, dict]] = []
        self._lock = threading.Lock()

    def schedule(self, delay: float, fn: Callable, *args, **kwargs):
        execute_at = time.time() + delay
        with self._lock:
            self._events.append((execute_at, fn, args, kwargs))
            self._events.sort(key=lambda e: e[0])

    def tick(self):
        """Execute all due events; return number executed."""
        now = time.time()
        executed = 0
        with self._lock:
            ready = [e for e in self._events if e[0] <= now]
            self._events = [e for e in self._events if e[0] > now]
        for ts, fn, args, kwargs in ready:
            try:
                fn(*args, **kwargs)
            except Exception as exc:  # noqa: broad-except – game loop should not crash
                print(f"[Scheduler] Error in scheduled task: {exc}")
            executed += 1
        return executed

    def next_wakeup(self) -> Optional[float]:
        with self._lock:
            return None if not self._events else max(0.0, self._events[0][0] - time.time())

# ---------------------------------------------------------------------------
# GameLoop Familiar
# ---------------------------------------------------------------------------

import importlib
from grimoire.familiars import register_familiar_class


def _base_cls():
    interpreter = importlib.import_module("grimoire.interpreter")  # type: ignore
    return getattr(interpreter, "GrimoireFamiliar")


@register_familiar_class("GameLoop")
class GameLoopFamiliar(_base_cls()):
    """Orchestrates scheduled events at a fixed frame-rate or on demand."""

    def __init__(self, name: str, loop_type: str = "real_time", fps: int = 60):
        super().__init__(name, "GameLoop", capabilities={})
        self.loop_type = loop_type  # "real_time" or "turn_based"
        self.fps = fps
        self.scheduler = Scheduler()
        self._thread: Optional[threading.Thread] = None
        self._running = False

        # sockets for external control (optional)
        self.add_socket("tick_output", direction="output")

    # ------------------------------------------------------------------
    def start(self):
        if self.loop_type == "real_time":
            if self._running:
                return "loop already running"
            self._running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            return "game loop started"
        else:
            return "turn-based loop ready (call tick manually)"

    def pause(self):
        self._running = False
        return "game loop paused"

    def resume(self):
        if self.loop_type == "real_time" and not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            return "game loop resumed"
        return "loop already running or not real_time"

    def tick(self):
        executed = self.scheduler.tick()
        self.send_to_socket("tick_output", executed)
        return executed

    def schedule(self, delay: float, fn: Callable, *args, **kwargs):
        self.scheduler.schedule(delay, fn, *args, **kwargs)
        return "event scheduled"

    # ------------------------------------------------------------------
    def _run_loop(self):
        interval = 1.0 / self.fps
        while self._running:
            start = time.time()
            self.tick()
            elapsed = time.time() - start
            sleep = max(0.0, interval - elapsed)
            time.sleep(sleep)