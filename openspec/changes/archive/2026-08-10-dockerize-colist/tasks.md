## 1\. Backend configuration surface

* [x] 1.1 Make CORS allowed origins configurable via an environment variable (e.g. `COLIST_CORS_ORIGINS`, comma-separated), defaulting to `http://localhost:5173` when unset
* [x] 1.2 Add a `GET /health` endpoint returning 200 once startup (`init_db`) has completed
* [x] 1.3 Document/set uvicorn proxy trust flags (`--proxy-headers`, `--forwarded-allow-ips`) for correct scheme detection behind a reverse proxy

## 2\. Session cookie security

* [x] 2.1 Update `get_or_create_session` (`backend/app/session.py`) to set `secure=True` on the cookie when the request scheme is `https`
* [x] 2.2 Verify the cookie is still set (without `Secure`) over local HTTP dev, and the session still works

## 3\. Static frontend serving

* [x] 3.1 Mount the built frontend (`frontend/dist`) as static files in the FastAPI app, served from the same origin as the API
* [x] 3.2 Add a catch-all fallback to `index.html` for non-API paths, so client-side routing (`react-router-dom`) works on full-page loads/refreshes of a list URL
* [x] 3.3 Confirm frontend API/WS calls work with a relative/same-origin base (`VITE_API_BASE` left unset in the image build)

## 4\. Dockerfile

* [x] 4.1 Write stage 1 (Node): install frontend dependencies, run `npm run build`
* [x] 4.2 Write stage 2 (Python): install backend dependencies from `requirements.txt`, copy the backend app and the built frontend `dist/` from stage 1
* [x] 4.3 Set image `ENV` defaults: `COLIST_DATABASE_URL=sqlite:////data/colist.db`; leave `COLIST_CORS_ORIGINS` unset (must be provided at runtime for production)
* [x] 4.4 Declare `/data` as a `VOLUME`; run the container process as a non-root user
* [x] 4.5 Add a `HEALTHCHECK` instruction targeting `/health`
* [x] 4.6 Set `CMD` to run uvicorn with a single worker and the proxy-header flags from 1.3
* [x] 4.7 Add `.dockerignore` (`node_modules`, `.venv`, `__pycache__`, `*.db`, `dist`, `.git`, `openspec`, etc.)

## 5\. Deployment documentation

* [x] 5.1 Document minimal `docker run` usage: port mapping, volume mount for `/data`, required/optional environment variables
* [x] 5.2 Document a VPS example: Caddy reverse proxy config in front of the container for automatic HTTPS
* [x] 5.3 Document a PaaS note: TLS handled natively by the platform; only environment variables and a persistent volume/disk need configuring
* [x] 5.4 Document the single-instance constraint explicitly (no multiple replicas or workers, and why)

## 6\. Verification

* [x] 6.1 Build the image locally and run it end to end: create a list, add/edit/remove items, verify real-time sync across two browser tabs
* [x] 6.2 Verify data persists across a container restart with the `/data` volume mounted, and is lost without it
* [x] 6.3 Verify CORS rejects an origin not in the configured allow-list
* [x] 6.4 Verify `/health` responds 200
* [x] 6.5 Verify the session cookie carries `Secure` when the app is run behind a local HTTPS-terminating proxy (e.g. Caddy) with the forwarded-proto flow, and does not block session creation when accessed over plain HTTP