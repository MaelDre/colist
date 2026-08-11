# ---- Stage 1: build the frontend ----
FROM node:20-alpine AS frontend-build

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

# Explicit empty string, not "unset" - see design.md (frontend calls the API
# via a same-origin relative path once served by the backend below).
ENV VITE_API_BASE=""
RUN npm run build

# ---- Stage 2: backend runtime, also serving the built frontend ----
FROM python:3.12-slim AS runtime

WORKDIR /app

RUN addgroup --system colist && adduser --system --ingroup colist colist \
    && apt-get update && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY --from=frontend-build /frontend/dist ./static
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV COLIST_DATABASE_URL=sqlite:////data/colist.db \
    COLIST_FORWARDED_ALLOW_IPS=* \
    PYTHONUNBUFFERED=1

# COLIST_CORS_ORIGINS is intentionally left unset here: the frontend is
# served from the same origin as the API in this image, so CORS only
# matters for callers hitting the API from a different origin, and there
# is no safe generic default for that in production - it must be set
# explicitly at deploy time if needed.

RUN chown -R colist:colist /app

# No VOLUME instruction here on purpose: Railway's Docker builder rejects
# it ("use Railway Volumes" instead). It isn't needed for functionality -
# a platform-level volume mount at /data (Railway Volumes, `docker run -v`,
# compose `volumes:`) works without it; see entrypoint.sh for how ownership
# of that mount is handled at runtime regardless of who created it.

# Stay root here - entrypoint.sh fixes /data ownership then drops to the
# non-root `colist` user itself (via gosu) before exec'ing the CMD below.
ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request as u; u.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/health')" || exit 1

# Single worker only: presence/WebSocket state (app/state.py, app/ws_manager.py)
# is in-memory and per-process - see design.md "Single-instance operation".
# --port reads $PORT when the platform assigns one (e.g. Railway), falling
# back to 8000 for `docker run` / VPS use where no PORT is set.
CMD uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 1 \
    --proxy-headers --forwarded-allow-ips "$COLIST_FORWARDED_ALLOW_IPS"
