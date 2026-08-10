## Context

Colist currently runs as two separate dev processes (Vite dev server on :5173, uvicorn on :8000) with CORS hardcoded for that pairing. There is no packaging, no production config surface, and no deployment documentation. The existing `add-collaborative-list` design already accepted a hard constraint that shapes this change: presence and WebSocket connection state (`state.py`, `ws_manager.py`) is in-memory and single-process, with no shared store — "would need a shared store (e.g. Redis) if scaled to multiple server processes." This change does not revisit that trade-off; it packages the app to run correctly within it.

Target deployment environments (decided during exploration): a VPS or a PaaS, not Kubernetes. Both are single-node-friendly, which lines up with the single-instance constraint rather than fighting it.

## Goals / Non-Goals

**Goals:**

* One image, one process, deployable via `docker run` (or one service in a PaaS) with minimal required configuration.
* The same image runs unmodified on a VPS or a PaaS — only environment variables and volume/proxy setup differ, never a rebuild.
* Session cookies are correctly `Secure` when served over HTTPS, however TLS is terminated.

**Non-Goals:**

* Horizontal scaling / multiple replicas or workers (still out of scope per the existing `add-collaborative-list` design.md).
* Migrating off SQLite to Postgres or any other database.
* TLS termination, certificate provisioning/renewal, or reverse proxy configuration inside the image.
* CI/CD pipeline or container registry publishing.
* Kubernetes manifests or any orchestrator-specific tooling.

## Decisions

### Single image, multi-stage build, backend serves the built frontend

Stage 1 (Node) runs `npm run build` to produce `frontend/dist`. Stage 2 (Python) installs backend dependencies and copies both the backend app and the built `dist/` output, mounting the static files in FastAPI alongside the existing API routers. Result: one image, one port, one process to run.

Alternative considered — two containers (nginx serving static frontend + separate backend container) behind a proxy: rejected. The backend is already constrained to a single instance, so there is no scaling benefit to splitting the two; splitting would only reintroduce the Vite `VITE_API_BASE` build-time/runtime mismatch problem (a static bundle built once would need per-environment rebuilds or a runtime env-injection mechanism to point at different API hosts). Serving both from the same origin sidesteps that problem entirely: the frontend calls the API via a relative path, with `VITE_API_BASE` explicitly set to an empty string at build time (not merely left unset — `frontend/src/api.js` originally used `||`, which treats an empty string the same as unset and falls back to `http://localhost:8000`; changed to `??` so an explicit empty value is honored as "same origin" while local dev without the variable set keeps its `localhost:8000` fallback).

### CORS origin(s) via environment variable

`CORSMiddleware`'s `allow_origins` is read from an environment variable (comma-separated list) at startup, defaulting to `http://localhost:5173` when unset so local dev behavior is unchanged. In production, since frontend and API share an origin, CORS only matters for tooling/alternate origins hitting the API directly — the variable must be set explicitly for any such case; there is no safe generic default for production.

### Database location: reuse the existing env override, no code change

`database.py` already reads `COLIST_DATABASE_URL` with a `sqlite:///./colist.db` default. Rather than changing that default in application code (which would also change local, non-Docker dev behavior), the Dockerfile sets `ENV COLIST_DATABASE_URL=sqlite:////data/colist.db` and declares `/data` as the volume mount point. Local dev outside Docker is unaffected; the image's default now points at a path meant to be volume-mounted, separate from application code.

### Health endpoint

A `GET /health` route returns 200 once the app has completed startup (after `init_db()` in the `lifespan` handler). Used both as a manual check and as the target of the image's `HEALTHCHECK` instruction. Kept intentionally minimal — no DB round-trip on every check, since SQLite availability is equivalent to filesystem availability of the mounted volume, not a separate failure mode worth probing per-request.

### Cookie `Secure` flag: derived from the request, not a manual toggle

`get_or_create_session` sets `secure=True` when the incoming request's scheme is `https`, rather than via a separate `COLIST_FORCE_SECURE_COOKIES`-style env flag. Alternative considered — explicit env flag: rejected because it's an extra manual step an operator can forget to set, or set inconsistently with the actual deployment topology (e.g. flips it on for a VPS deployment that isn't actually behind TLS yet, silently breaking cookie-setting). Deriving from the request scheme is self-consistent by construction, provided the scheme is correctly known — which requires the next decision.

### Trust forwarded scheme from the reverse proxy

Since TLS is terminated outside the container, FastAPI/uvicorn only sees plain HTTP internally by default, which would make the request-scheme-derived `Secure` logic always resolve to non-secure. uvicorn is started with `--proxy-headers` and a `--forwarded-allow-ips` value scoped to the known proxy (the PaaS's internal LB, or the VPS's local Caddy instance), so `X-Forwarded-Proto: https` set by the terminator is honored and the app sees the original scheme correctly.

### Single-instance operation, enforced by the image's own CMD

The Dockerfile's `CMD` runs a single uvicorn worker — no `--workers N`, no gunicorn process manager. This isn't just a default operators are trusted to preserve; it's the only supported invocation shipped by the image, because `state.py`/`ws_manager.py` remain in-memory and unchanged by this proposal. Deployment docs state explicitly that running multiple replicas of this image against the same list will produce inconsistent presence and missed broadcasts.

### TLS stays outside the image

Confirmed from exploration: a PaaS terminates TLS natively at its load balancer, requiring no image-level change. A VPS deployment adds a separate, non-bundled reverse proxy (Caddy recommended for its automatic Let's Encrypt handling and minimal config) in front of the container. This keeps the application image free of certificate lifecycle logic, which would otherwise be the largest source of complexity in an image whose explicit goal is to stay simple to run.

## Risks / Trade-offs

* **[Risk]** The `Secure`-cookie-from-request-scheme logic depends on the reverse proxy correctly setting `X-Forwarded-Proto` and on `--forwarded-allow-ips` being scoped to the actual proxy → **Mitigation**: document the required Caddy/PaaS proxy header behavior and the `--forwarded-allow-ips` value explicitly in deployment docs; a misconfigured or untrusted-IP setup fails safe (cookie simply won't be marked Secure, degrading to current behavior rather than an open vulnerability).
* **[Risk]** SQLite on a single mounted volume has no built-in backup or replication story → **Mitigation**: accepted for v1 (matches the existing SQLite decision in `add-collaborative-list`); note in deployment docs that periodic file-level backup of the volume is the operator's responsibility.
* **[Trade-off]** Bundling frontend and backend into one image couples their release cadence and rules out independent scaling → accepted: the backend was already constrained to a single instance by its in-memory state, so independent scaling was never available; bundling costs nothing in practice and removes the `VITE_API_BASE` per-environment problem entirely.
* **[Trade-off]** No CI/CD or registry publishing in this change means the image must be built manually (or via a separate follow-up) wherever it's deployed → accepted, explicitly out of scope.

## Migration Plan

Not applicable — no existing deployed instance. Local, non-Docker development is unaffected: `COLIST_DATABASE_URL` and CORS origin both keep their current defaults when the app is run outside the image.
