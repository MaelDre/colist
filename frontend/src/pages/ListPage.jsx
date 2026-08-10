import { useParams } from "react-router-dom";
import { useListSocket } from "../hooks/useListSocket";
import PresenceBar from "../components/PresenceBar";
import ItemRow from "../components/ItemRow";
import AddItemForm from "../components/AddItemForm";
import DeleteListButton from "../components/DeleteListButton";

export default function ListPage() {
  const { listId } = useParams();
  const { status, items, presence, highlighted, connected } = useListSocket(listId);

  if (status === "loading") {
    return <p className="status-message">Loading list…</p>;
  }

  if (status === "not_found") {
    return (
      <div className="status-message">
        <h2>List not found</h2>
        <p>This list doesn't exist, or it may have been deleted.</p>
      </div>
    );
  }

  return (
    <div className="list-page">
      <header className="list-header">
        <PresenceBar presence={presence} />
        {!connected && <span className="offline-badge">Reconnecting…</span>}
        <DeleteListButton listId={listId} />
      </header>

      <ul className="item-list">
        {items.map((item) => (
          <ItemRow key={item.id} listId={listId} item={item} highlighted={highlighted.has(item.id)} />
        ))}
        {items.length === 0 && <li className="empty-state">No items yet — add the first one below.</li>}
      </ul>

      <AddItemForm listId={listId} />
    </div>
  );
}
