const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";
const WS_BASE = API_BASE.replace(/^http/, "ws");

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: options.body ? { "Content-Type": "application/json" } : undefined,
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      // response had no JSON body
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

export function createList() {
  return request("/api/lists", { method: "POST" });
}

export function fetchList(listId) {
  return request(`/api/lists/${listId}`);
}

export function deleteList(listId) {
  return request(`/api/lists/${listId}`, { method: "DELETE" });
}

export function addItem(listId, payload) {
  return request(`/api/lists/${listId}/items`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function editItem(listId, itemId, payload) {
  return request(`/api/lists/${listId}/items/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function removeItem(listId, itemId) {
  return request(`/api/lists/${listId}/items/${itemId}`, { method: "DELETE" });
}

export function wsUrl(listId) {
  return `${WS_BASE}/api/lists/${listId}/ws`;
}
