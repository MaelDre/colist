## Why

Items support an optional free-text description, but in practice it isn't used and doesn't carry its weight: it adds a field to every add/edit form, every API payload, and every broadcast message for little value. Removing it simplifies the item model.

## What Changes

* <strong>BREAKING</strong>: Remove the `description` field from items entirely - it can no longer be set, edited, or read via the API.
* Remove `description` from `ItemCreate`, `ItemUpdate`, and `ItemOut` (backend/app/schemas.py).
* Remove the `description` column from `Item` (backend/app/models.py). The app has no migration framework (SQLAlchemy `Base.metadata.create_all` runs at startup only, and never alters existing tables), so a small idempotent startup step drops the leftover `description` column from any already-deployed database. This is required, not optional: the column is `NOT NULL` with no DB-level default, so leaving it in place would break every item insert as soon as the ORM stopped populating it.
* Remove `description` read/write from the add-item and edit-item routes (backend/app/routers/items.py). This also removes it from the WebSocket broadcast payloads, since those are built from `ItemOut`.
* Remove the description input from the add-item form and the description textarea/display from the item row (frontend/src/components/AddItemForm.jsx, frontend/src/components/ItemRow.jsx), and the associated `.item-description` CSS rule (frontend/src/App.css).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

* `list-items`: Items no longer carry a description. The "Add an item" and "Edit an item" requirements drop all description-related behavior; items are add/edited/removed by name only.

## Impact

* Backend: `models.py`, `schemas.py`, `routers/items.py`, `database.py` (startup column drop).
* Frontend: `AddItemForm.jsx`, `ItemRow.jsx`, `App.css`.
* Data: any `description` values already stored in the production SQLite database are dropped along with the column on next startup. Acceptable since the user is currently the only production user.
* No test suite exists in this repo, so no tests are affected.