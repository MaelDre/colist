## Context

Greenfield project — no existing code, specs, or infrastructure. Stack is fixed as Python backend / React frontend (per README). See proposal.md for motivation. Key constraint shaping this design: no accounts or auth of any kind — the list URL itself is the only access control, and identity is purely a per-browser, per-list convenience for attributing edits.

## Goals / Non-Goals

**Goals:**

* Real-time propagation of item changes that feels instant to a small group (a handful of concurrent editors per list), without building character-level collaborative text editing.
* Keep conflict handling simple and predictable (last-write-wins) rather than introducing OT/CRDT machinery the feature set doesn't need.
* Make the storage layer swappable (SQLite now, Postgres/MySQL later) without an early migration project.

**Non-Goals:**

* Live keystroke-by-keystroke collaborative text editing within a single field (no OT/CRDT).
* Any form of accounts, login, or persistent cross-list identity.
* List/edit history, undo, or recovery of deleted data.
* Horizontal scaling / multi-node WebSocket fan-out (single-process broadcast is sufficient for v1).

## Decisions

### Sync transport: WebSocket broadcast, not OT/CRDT

The collaboration surface is coarse-grained (item name/description, edited as discrete submit actions), not fine-grained prose editing. A server that broadcasts "item X changed" events to all connected clients for a list, combined with last-write-wins on the persisted record, gives the real-time feel the README asks for ("Etherpad-style" attribution) without the correctness complexity of operational transforms or CRDT merge logic. Alternative considered: Yjs/Automerge CRDT — rejected as solving a problem (concurrent character-level merges) this app doesn't have; would add a real dependency and conceptual overhead for no user-visible benefit given edit-and-commit semantics.

### Conflict resolution: last-write-wins by server receipt order

Concurrent edits to the same item are rare (different people typically edit different items) and low-stakes (a shopping/todo-style list, not a legal document). The server treats the last write it receives as canonical, persists it, and broadcasts it; the losing edit is silently superseded. No merge, no versioning, no operational log.

### Identity: server-issued opaque session cookie, scoped per list

On first access to a list, the server issues an HTTP cookie scoped to that list's path (or otherwise namespaced by list ID) containing an opaque session token, and assigns a color to that token server-side. The cookie is reused across tabs/reloads in the same browser (session dedupe for presence), and is independent per list (visiting list B does not reuse list A's session or color). No client-generated identity — the server is the source of truth for session-to-color mapping so it can also drive presence counts.

### Presence tracking: connection-count per session, in-memory

The server keeps an in-memory map of `session_id -> set of open WebSocket connections` per list. Presence indicator = one entry per session with at least one open connection. Joining is "first connection for this session in this list opens"; leaving is "last connection for this session in this list closes." No persistence needed — presence is inherently ephemeral and resets cleanly on server restart.

### List/URL identifier: UUID

UUIDs are the entire access-control mechanism (no auth layer), so they must be unguessable — a random 122-bit UUID4 is the simple, standard choice over a shorter human-friendly slug, trading URL prettiness for not needing to reason about brute-force enumeration.

### Reconnect protocol: fetch-then-subscribe

Every client, on initial load and on any reconnect, calls the list's HTTP GET endpoint for full current state, then opens/resubscribes its WebSocket. The WebSocket is never treated as the source of truth by itself — it's a live-update stream layered on top of state that was just confirmed via HTTP. This avoids needing an event replay/backlog mechanism on the server; a missed event is irrelevant because the next reconnect re-fetches everything.

### Storage: SQLite behind an ORM abstraction

SQLite is sufficient for v1 (single file, no ops overhead) but the proposal already anticipates a Postgres/MySQL move. Using an ORM (e.g. SQLAlchemy) from the start, and avoiding SQLite-specific SQL or features in application code, keeps that future migration a config/driver change rather than a rewrite.

## Risks / Trade-offs

* **[Risk]** Last-write-wins silently discards a losing concurrent edit with no warning to the user who made it → <strong>Mitigation</strong>: acceptable given low edit-collision likelihood and low stakes of this data; not mitigated further in v1 (no "your edit was overwritten" notice), but worth revisiting if real usage shows frequent collisions.
* **[Risk]** In-memory presence/connection state means a server restart or process crash silently drops all presence info (clients will reconnect and repopulate it, but there's a gap) → <strong>Mitigation</strong>: acceptable for v1 single-process deployment; would need a shared store (e.g. Redis) if scaled to multiple server processes.
* **[Risk]** UUID-based unguessable URLs are the only access control — if a URL leaks (e.g. via browser history sync, referrer headers, shared screenshots), anyone who obtains it has full read/write/delete access with no way to revoke access short of deleting the list → <strong>Mitigation</strong>: accepted as an explicit product tradeoff (see proposal); no mitigation planned for v1.
* **[Trade-off]** No list/item history or undo means any edit or deletion is permanent, including accidental ones → accepted per explore-phase decision to keep v1 simple.

## Migration Plan

Not applicable — greenfield change, no prior system or data to migrate from.