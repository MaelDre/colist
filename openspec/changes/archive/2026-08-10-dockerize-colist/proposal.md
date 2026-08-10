## Why

Colist has no way to be deployed today: no Dockerfile, no production configuration, and several dev-only assumptions baked into the code (CORS hardcoded to `http://localhost:5173`, session cookies never marked `Secure`, frontend/backend served as two separate dev servers). The goal is to make the app deployable with a single command, on a VPS or a PaaS, without adding infrastructure the app's actual constraints don't need — no Postgres, no horizontal scaling, no TLS handling inside the image.

## What Changes

* Package backend and frontend into a single multi-stage Docker image: stage 1 builds the Vite frontend, stage 2 is the Python/FastAPI runtime that also serves the built static frontend, so API and frontend are served from the same origin and port.
* Make the CORS allowed origin(s) configurable via an environment variable instead of hardcoded to `localhost:5173`.
* Point the image's default SQLite database file at a dedicated, volume-mountable directory (via the existing `COLIST_DATABASE_URL` override — no backend code change needed for this).
* Add a health-check endpoint and wire it into the image's `HEALTHCHECK`.
* Make session cookies conditionally `Secure`, derived from the request's scheme, and configure uvicorn to trust forwarded-proto headers so this works correctly behind a TLS-terminating reverse proxy or PaaS load balancer.
* Add `.dockerignore`.
* Explicitly document, as a deployment requirement, the single-instance constraint already decided in `add-collaborative-list`'s design (in-memory presence/WebSocket state): one process, one worker, no replicas.
* Add minimal deployment documentation: running the image directly, a VPS example using Caddy as an external TLS-terminating reverse proxy, and a note on PaaS deployment (TLS handled natively by the platform).

## Capabilities

### New Capabilities

* `deployment`: packaging the app as a single container image, its runtime configuration surface (CORS origin, database location, health reporting), and the operational constraints that follow from the app's single-process design (no horizontal scaling, TLS terminated outside the image).

### Modified Capabilities

* `session-identity`: the session cookie requirement gains explicit HTTPS-awareness (the `Secure` attribute), needed for safe production deployment behind TLS.

## Impact

* Backend: `main.py` (CORS origins from env), `session.py` (conditional `Secure` cookie), new `/health` route, static file mounting for the built frontend, uvicorn startup flags (`--proxy-headers`, `--forwarded-allow-ips`, single worker).
* New files: `Dockerfile` (multi-stage), `.dockerignore`, deployment docs.
* Small frontend fix: `frontend/src/api.js` used `||` to fall back to `http://localhost:8000`, which also overrode an explicitly empty `VITE_API_BASE`. Changed to `??` so the Docker build can pass an explicit empty value to mean same-origin, while local dev (`VITE_API_BASE` truly unset) keeps its `localhost:8000` fallback.
* No change to `backend/app/database.py` — the existing `COLIST_DATABASE_URL` override is reused; only the image sets a different default value.
* Out of scope: Postgres migration, multi-instance/horizontal scaling, Kubernetes, TLS certificate handling inside the image, CI/CD or registry publishing.
