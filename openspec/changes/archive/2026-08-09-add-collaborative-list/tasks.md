## 1. Project setup

- [x] 1.1 Scaffold Python backend project (dependency management, app entrypoint, dev server)
- [x] 1.2 Scaffold React frontend project (build tooling, dev server)
- [x] 1.3 Add SQLite + ORM (e.g. SQLAlchemy) dependency and configure a database connection module that does not use SQLite-specific SQL in application code

## 2. Data model & storage

- [x] 2.1 Define `List` model: UUID primary key, created timestamp
- [x] 2.2 Define `Item` model: id, list foreign key, name, description, last-edited-by color, last-edited-at timestamp
- [x] 2.3 Write schema migration/creation for both tables

## 3. List lifecycle API

- [x] 3.1 Implement `POST` create-list endpoint: generates UUID, persists empty list, returns its URL/id
- [x] 3.2 Implement `GET` list endpoint: returns list content by UUID, 404 for unknown UUID
- [x] 3.3 Implement `DELETE` list endpoint: permanently removes list and its items
- [x] 3.4 Implement frontend delete-confirmation step gating the delete request

## 4. List items API

- [x] 4.1 Implement `POST` add-item endpoint: requires name, optional description, rejects missing name
- [x] 4.2 Implement `PATCH`/`PUT` edit-item endpoint: updates name and/or description
- [x] 4.3 Implement `DELETE` item endpoint: removes an item from its list

## 5. Session identity

- [x] 5.1 Implement server-issued session cookie scoped per list, created on first access to a given list
- [x] 5.2 Implement server-side session-id-to-color assignment (random color, stable for the session's lifetime)
- [x] 5.3 Verify cookie scoping keeps sessions independent across different lists (no cross-list identity)

## 6. Real-time collaboration (backend)

- [x] 6.1 Implement WebSocket endpoint for a list, accepting connections tagged with the visitor's session id
- [x] 6.2 Broadcast item add/edit/remove events to all connected clients for that list
- [x] 6.3 Apply last-write-wins on the server: persist and broadcast the last-received edit to an item, discard superseded concurrent writes
- [x] 6.4 Stamp each item with last-edited-by color and timestamp on every add/edit, included in broadcast payloads

## 7. Presence tracking (backend)

- [x] 7.1 Maintain in-memory per-list map of session id → set of open WebSocket connections
- [x] 7.2 Broadcast presence-join when a session's first connection to a list opens
- [x] 7.3 Broadcast presence-leave when a session's last connection to a list closes
- [x] 7.4 Include current presence snapshot in the initial HTTP list-fetch response

## 8. Frontend: list view & item CRUD

- [x] 8.1 Build create-list flow (button/action → navigate to new list's URL)
- [x] 8.2 Build list view rendering items (name, description)
- [x] 8.3 Build add/edit/remove item UI wired to the REST endpoints
- [x] 8.4 Build not-found state for unknown list URLs
- [x] 8.5 Build delete-list flow with confirmation dialog

## 9. Frontend: real-time sync & reconnect

- [x] 9.1 On list load, fetch full state via HTTP before opening the WebSocket connection
- [x] 9.2 Subscribe to WebSocket updates after initial fetch completes; apply incoming item events to local state
- [x] 9.3 On WebSocket disconnect, detect the drop and re-fetch full state via HTTP before resubscribing on reconnect
- [x] 9.4 Render the edit-attribution color highlight on an item when it changes, and fade it out after a short delay

## 10. Frontend: presence

- [x] 10.1 Render presence indicator (colored dots) from the initial fetch snapshot
- [x] 10.2 Update presence indicator live on join/leave WebSocket events
- [x] 10.3 Verify multiple tabs in the same browser produce one presence entry, not one per tab

## 11. End-to-end verification

- [x] 11.1 Verify: create list, share URL, two clients editing concurrently see each other's changes live (scripted WebSocket test against the running dev backend, not a real browser - see note)
- [x] 11.2 Verify: same browser two tabs share one session/color and one presence entry (scripted, same caveat)
- [ ] 11.3 Manually verify: killing network mid-session and restoring it resyncs correctly via reconnect protocol (needs a real browser; not run this session)
- [x] 11.4 Verify: delete-list frontend flow requires confirmation before calling the API (code path traced; not clicked in a real browser)
