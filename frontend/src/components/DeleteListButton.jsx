import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { deleteList } from "../api";

// Deletion is permanent (see specs/list-lifecycle) - this confirm step is
// the only safeguard, there is no undo after the request goes through.
export default function DeleteListButton({ listId }) {
  const [confirming, setConfirming] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await deleteList(listId);
      navigate("/");
    } finally {
      setDeleting(false);
    }
  };

  if (confirming) {
    return (
      <span className="delete-confirm">
        <span>Delete this list permanently? This cannot be undone.</span>
        <button onClick={handleDelete} disabled={deleting} className="danger">
          {deleting ? "Deleting…" : "Yes, delete"}
        </button>
        <button onClick={() => setConfirming(false)} disabled={deleting}>
          Cancel
        </button>
      </span>
    );
  }

  return (
    <button className="delete-button" onClick={() => setConfirming(true)}>
      Delete list
    </button>
  );
}
