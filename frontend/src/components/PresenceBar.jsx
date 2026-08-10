export default function PresenceBar({ presence }) {
  const entries = Array.from(presence.entries());
  return (
    <div className="presence-bar" title={`${entries.length} connected`}>
      {entries.map(([sessionId, color]) => (
        <span key={sessionId} className="presence-dot" style={{ backgroundColor: color }} />
      ))}
    </div>
  );
}
