import json
from pathlib import Path
from typing import Any, Dict, Optional


class DashboardStateStore:
    def __init__(self, state_file: Optional[Path] = None) -> None:
        if state_file is None:
            state_file = Path(__file__).resolve().parent.parent / "dashboard" / "state.json"
        self.state_file = state_file
        self._ensure_file()

    def _ensure_file(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.state_file.exists():
            self.write_state(
                status="idle",
                mode="sleep",
                activity="Awaiting wake word",
                last_command="",
                last_response="",
            )

    def write_state(
        self,
        status: str,
        mode: str,
        activity: str,
        last_command: str = "",
        last_response: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "status": status,
            "mode": mode,
            "activity": activity,
            "last_command": last_command,
            "last_response": last_response,
            "updated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        }

        if self.state_file.exists() and details is None:
            try:
                with self.state_file.open("r", encoding="utf-8") as handle:
                    current_state = json.load(handle)
                if "details" in current_state:
                    payload["details"] = current_state["details"]
            except Exception:
                pass

        if details:
            payload["details"] = details

        with self.state_file.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

        return payload

    def load_state(self) -> Dict[str, Any]:
        if not self.state_file.exists():
            self._ensure_file()
        with self.state_file.open("r", encoding="utf-8") as handle:
            return json.load(handle)


dashboard_store = DashboardStateStore()


def update_dashboard_state(
    status: str,
    mode: str,
    activity: str,
    last_command: str = "",
    last_response: str = "",
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return dashboard_store.write_state(
        status=status,
        mode=mode,
        activity=activity,
        last_command=last_command,
        last_response=last_response,
        details=details,
    )
