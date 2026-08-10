import { useState } from "react";
import { editItem, removeItem } from "../api";

export default function ItemRow({ listId, item, highlighted }) {
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(item.name);
  const [description, setDescription] = useState(item.description);
  const [saving, setSaving] = useState(false);

  const startEdit = () => {
    setName(item.name);
    setDescription(item.description);
    setEditing(true);
  };

  const save = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    try {
      await editItem(listId, item.id, { name: name.trim(), description });
      setEditing(false);
    } finally {
      setSaving(false);
    }
  };

  const remove = () => {
    removeItem(listId, item.id);
  };

  if (editing) {
    return (
      <li className="item-row editing">
        <form onSubmit={save}>
          <input value={name} onChange={(e) => setName(e.target.value)} autoFocus />
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} />
          <div className="item-actions">
            <button type="submit" disabled={saving || !name.trim()}>
              Save
            </button>
            <button type="button" onClick={() => setEditing(false)}>
              Cancel
            </button>
          </div>
        </form>
      </li>
    );
  }

  return (
    <li
      className={`item-row${highlighted ? " highlighted" : ""}`}
      style={highlighted ? { "--highlight-color": item.last_edited_by_color } : undefined}
    >
      <div className="item-content" onClick={startEdit}>
        <span className="item-name">{item.name}</span>
        {item.description && <span className="item-description">{item.description}</span>}
      </div>
      <button className="remove-button" onClick={remove} aria-label={`Remove ${item.name}`}>
        ×
      </button>
    </li>
  );
}
