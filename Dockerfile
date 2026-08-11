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

RUN addgroup --system colist && adduser --system --ingroup colist colist

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY --from=frontend-build /frontend/dist ./static

ENV COLIST_DATABASE_URL=sqlite:////data/colist.db \
    COLIST_FORWARDED_ALLOW_IPS=* \
    PYTHONUNBUFFERED=1

# COLIST_CORS_ORIGINS is intentionally left unset here: the frontend is
# served from the same origin as the API in this image, so CORS only
# matters for callers hitting the API from a different origin, and there
# is no safe generic default for that in production - it must be set
# explicitly at deploy time if needed.

RUN mkdir -p /data && chown -R colist:colist /data /app
# line below is commented in order to make the deployment on railway working
# VOLUME ["/data"]

USER colist

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

# Single worker only: presence/WebSocket state (app/state.py, app/ws_manager.py)
# is in-memory and per-process - see design.md "Single-instance operation".
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 \
    --proxy-headers --forwarded-allow-ips "$COLIST_FORWARDED_ALLOW_IPS"
