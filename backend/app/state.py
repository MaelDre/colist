"""In-memory, per-list session/color/presence bookkeeping.

Deliberately ephemeral (see design.md - Presence tracking): this all
resets cleanly on server restart, which is an accepted trade-off for v1.
"""

import random
import secrets

COLOR_PALETTE = [
    "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
    "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
    "#008080", "#e6beff",
]


class ListState:
    def __init__(self) -> None:
        self.session_colors: dict[str, str] = {}
        self.connections: dict[str, set] = {}

    def color_for(self, session_id: str) -> str:
        if session_id not in self.session_colors:
            self.session_colors[session_id] = random.choice(COLOR_PALETTE)
        return self.session_colors[session_id]

    def presence_snapshot(self) -> list[dict]:
        return [
            {"session_id": sid, "color": self.session_colors.get(sid, "")}
            for sid, conns in self.connections.items()
            if conns
        ]


class ListStateStore:
    def __init__(self) -> None:
        self._lists: dict[str, ListState] = {}

    def get(self, list_id: str) -> ListState:
        if list_id not in self._lists:
            self._lists[list_id] = ListState()
        return self._lists[list_id]

    def drop(self, list_id: str) -> None:
        self._lists.pop(list_id, None)


store = ListStateStore()


def new_session_id() -> str:
    return secrets.token_urlsafe(16)
