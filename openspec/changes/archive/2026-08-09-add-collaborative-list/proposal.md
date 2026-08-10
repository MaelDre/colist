## Why

Colist needs its first working slice: a way for a group of people to create a shared list, reach it via a single unguessable URL, and edit it together in real time — without accounts, logins, or any signup friction. This is the foundational change; nothing exists yet.

## What Changes

* Introduce list creation, producing a UUID-based URL that is the sole access control (no accounts, no passwords).
* Introduce list viewing and hard deletion (with a confirmation step; deletion is permanent, no recovery).
* Introduce items within a list: add, edit, and remove, each with a name and an optional description.
* Introduce a cookie-based session identity, scoped per-list, that assigns each visitor a random color.
* Introduce real-time collaboration: edits broadcast over WebSocket to everyone viewing the list, using last-write-wins conflict resolution (not live keystroke-level merging). Each item shows a fading highlight in the color of whoever last edited it.
* Introduce a presence indicator showing colored dots for everyone currently connected to the list, deduplicated per session (multiple tabs in the same browser count once).
* Define the reconnect behavior: a client (re)connecting always fetches full current state over HTTP before subscribing to the WebSocket, so it never relies on the socket alone as source of truth.

## Capabilities

### New Capabilities

* `list-lifecycle`: Creating a list (UUID URL), viewing a list by URL, and permanently deleting a list with confirmation.
* `list-items`: Adding, editing, and removing items (name + description) within a list.
* `session-identity`: Cookie-based, per-list session identity with random color assignment, and the presence indicator showing who is currently connected.
* `realtime-collaboration`: Broadcasting item changes to all connected clients over WebSocket, last-write-wins conflict resolution, per-edit color highlighting, and the fetch-then-subscribe reconnect protocol.

### Modified Capabilities

(none — greenfield change, no existing specs)

## Impact

* New Python backend: REST endpoints for list/item CRUD, WebSocket endpoint for broadcast, SQLite-backed persistence behind an ORM (to allow a later Postgres/MySQL swap).
* New React frontend: list view/edit UI, WebSocket client with reconnect-resync logic, presence and edit-highlight rendering.
* New data model: lists, items, and ephemeral session/color state.
* No existing systems affected — this is the first change in the project.