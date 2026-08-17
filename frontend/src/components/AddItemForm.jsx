import { useState } from "react";
import { addItem } from "../api";

export default function AddItemForm({ listId }) {
  const [name, setName] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSubmitting(true);
    try {
      await addItem(listId, { name: name.trim() });
      setName("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="add-item-form" onSubmit={submit}>
      <input placeholder="Item name" value={name} onChange={(e) => setName(e.target.value)} />
      <button type="submit" disabled={submitting || !name.trim()}>
        Add item
      </button>
    </form>
  );
}
