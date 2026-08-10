import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createList } from "../api";

export default function HomePage() {
  const navigate = useNavigate();
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);

  const handleCreate = async () => {
    setCreating(true);
    setError(null);
    try {
      const { id } = await createList();
      navigate(`/list/${id}`);
    } catch {
      setError("Could not create a list. Please try again.");
      setCreating(false);
    }
  };

  return (
    <div className="home">
      <h1>colist</h1>
      <p>Create a shared list and send the link to anyone you want to collaborate with.</p>
      <button onClick={handleCreate} disabled={creating}>
        {creating ? "Creating…" : "Create a new list"}
      </button>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
