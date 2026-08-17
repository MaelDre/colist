## 1\. Backend

* [x] 1.1 Remove the `description` column from `Item` in backend/app/models.py
* [x] 1.2 Remove `description` from `ItemCreate`, `ItemUpdate`, and `ItemOut` in backend/app/schemas.py
* [x] 1.3 Remove `description` read/write in `add_item` and `edit_item` in backend/app/routers/items.py
* [x] 1.4 Add an idempotent startup step in backend/app/database.py that drops the leftover `description` column from `items` on databases created before this change (required: the column is `NOT NULL` with no DB-level default, so leaving it would break every insert)

## 2\. Frontend

* [x] 2.1 Remove the description input and its state from frontend/src/components/AddItemForm.jsx
* [x] 2.2 Remove the description textarea, its state, and the display span from frontend/src/components/ItemRow.jsx
* [x] 2.3 Remove the `.item-description` rule from frontend/src/App.css

## 3\. Verification

* [x] 3.1 Start backend and frontend locally; add an item, edit its name, remove it - confirm no description field appears anywhere and nothing errors