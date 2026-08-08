"""Small state bridge used by the local Astra Dashboard."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from queue import Empty, Queue
from threading import Lock
from typing import Any


class DashboardStateStore:
    def __init__(self) -> None:
        self.path = Path(__file__).resolve().parent.parent / "dashboard" / "state.json"
        self._lock = Lock()

    def update(self, **changes: Any) -> None:
        with self._lock:
            state = self._read()
            state.update({key: value for key, value in changes.items() if value is not None})
            updated_at = datetime.now(timezone.utc).isoformat()
            state["updated_at"] = updated_at
            reply = changes.get("last_response")
            if reply:
                state["live_response"] = ""
            state.pop("reply_history", None)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(state, indent=2) + "\n")

    def _read(self) -> dict[str, Any]:
        try:
            return json.loads(self.path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "status": "offline",
                "activity": "Astra has not started yet.",
                "last_command": "",
                "last_response": "",
            }


dashboard_state = DashboardStateStore()
dashboard_commands: Queue[str] = Queue()


def update_dashboard_state(
    *,
    status: str | None = None,
    activity: str | None = None,
    last_command: str | None = None,
    last_response: str | None = None,
    live_response: str | None = None,
) -> None:
    """Publish the latest assistant state for the local dashboard."""
    dashboard_state.update(
        status=status,
        activity=activity,
        last_command=last_command,
        last_response=last_response,
        live_response=live_response,
    )


def enqueue_dashboard_command(command: str) -> bool:
    """Queue a command submitted from the local dashboard."""
    active_state = dashboard_state._read()
    is_briefing = any(
        phrase in command.lower()
        for phrase in ("good morning", "daily briefing", "morning briefing")
    )
    if (
        is_briefing
        and active_state.get("status") == "responding"
        and active_state.get("live_response")
    ):
        return False
    dashboard_commands.put(command.strip())
    update_dashboard_state(
        status="processing",
        activity="Dashboard command received.",
        last_command=command.strip(),
        live_response=f"Working on: {command.strip()}",
    )
    return True


def get_dashboard_command(timeout: float | None = None) -> str | None:
    """Return the next dashboard command, optionally waiting for one."""
    try:
        if timeout is None:
            return dashboard_commands.get_nowait()
        return dashboard_commands.get(timeout=timeout)
    except Empty:
        return None
