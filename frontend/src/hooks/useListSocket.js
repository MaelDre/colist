import { useCallback, useEffect, useRef, useState } from "react";
import { fetchList, wsUrl } from "../api";

const HIGHLIGHT_FADE_MS = 4000;
const RECONNECT_DELAY_MS = 1500;

// Backs the list view: fetches full state over HTTP, then subscribes to a
// WebSocket for live updates. Every (re)connect re-fetches full state first
// (see design.md - Reconnect protocol), so a missed event while offline is
// never permanently lost.
export function useListSocket(listId) {
  const [status, setStatus] = useState("loading"); // loading | ready | not_found | error
  const [items, setItems] = useState([]);
  const [presence, setPresence] = useState(new Map()); // session_id -> color
  const [highlighted, setHighlighted] = useState(new Map()); // item_id -> true
  const [connected, setConnected] = useState(false);

  const timersRef = useRef(new Map());

  const flashHighlight = useCallback((itemId) => {
    const timers = timersRef.current;
    setHighlighted((prev) => new Map(prev).set(itemId, true));
    const existing = timers.get(itemId);
    if (existing) clearTimeout(existing);
    timers.set(
      itemId,
      setTimeout(() => {
        setHighlighted((prev) => {
          const next = new Map(prev);
          next.delete(itemId);
          return next;
        });
        timers.delete(itemId);
      }, HIGHLIGHT_FADE_MS),
    );
  }, []);

  useEffect(() => {
    let cancelled = false;
    let ws = null;
    let reconnectTimer = null;
    const timers = timersRef.current;

    const applyMessage = (msg) => {
      switch (msg.type) {
        case "item_added":
        case "item_edited":
          setItems((prev) => {
            const idx = prev.findIndex((it) => it.id === msg.item.id);
            if (idx === -1) return [...prev, msg.item];
            const next = [...prev];
            next[idx] = msg.item;
            return next;
          });
          flashHighlight(msg.item.id);
          break;
        case "item_removed":
          setItems((prev) => prev.filter((it) => it.id !== msg.item_id));
          break;
        case "presence_join":
          setPresence((prev) => new Map(prev).set(msg.session_id, msg.color));
          break;
        case "presence_leave":
          setPresence((prev) => {
            const next = new Map(prev);
            next.delete(msg.session_id);
            return next;
          });
          break;
        default:
          break;
      }
    };

    const connect = async () => {
      try {
        const data = await fetchList(listId);
        if (cancelled) return;
        setItems(data.items);
        setPresence(new Map(data.presence.map((p) => [p.session_id, p.color])));
        setStatus("ready");
      } catch (err) {
        if (cancelled) return;
        if (err.status === 404) {
          setStatus("not_found");
          return;
        }
        setStatus("error");
        reconnectTimer = setTimeout(connect, RECONNECT_DELAY_MS);
        return;
      }

      ws = new WebSocket(wsUrl(listId));
      ws.onopen = () => {
        if (!cancelled) setConnected(true);
      };
      ws.onmessage = (event) => {
        if (!cancelled) applyMessage(JSON.parse(event.data));
      };
      ws.onclose = () => {
        if (cancelled) return;
        setConnected(false);
        reconnectTimer = setTimeout(connect, RECONNECT_DELAY_MS);
      };
      ws.onerror = () => {
        ws?.close();
      };
    };

    setStatus("loading");
    setItems([]);
    setPresence(new Map());
    connect();

    return () => {
      cancelled = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) {
        ws.onclose = null;
        ws.close();
      }
      for (const timer of timers.values()) clearTimeout(timer);
      timers.clear();
    };
  }, [listId, flashHighlight]);

  return { status, items, presence, highlighted, connected };
}
