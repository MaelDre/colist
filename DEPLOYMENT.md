# Deploying colist

colist ships as a single Docker image: a multi-stage build produces the React
frontend and bundles it alongside the FastAPI backend, which serves both the
API/WebSocket routes and the built frontend from the same origin and port.

## Build

```
docker build -t colist .
```

## Run it directly

```
docker run -d \
  --name colist \
  -p 8000:8000 \
  -v colist-data:/data \
  -e COLIST_CORS_ORIGINS=https://your-domain.example \
  colist
```

* `-v colist-data:/data` persists the SQLite database (`/data/colist.db`)
    across container restarts/recreations. Without it, all lists are lost the
    moment the container is removed.
* `COLIST_CORS_ORIGINS` only matters if something calls the API from a
    *different* origin than the one serving the frontend (the normal case, one
    origin for both, needs no CORS configuration at all). Comma-separate
    multiple origins if needed.
* The container always serves plain HTTP on port 8000. TLS is not handled
    inside the image - see below.

The image exposes a health check at `GET /health` (also wired into the
image's own `HEALTHCHECK` instruction).

## Single instance only

Do not run more than one replica/container of this image against the same
deployment, and do not increase the worker count. Presence indicators and
real-time item sync are held in an in-memory, per-process store (see
`design.md` in the `dockerize-colist` and `add-collaborative-list` changes);
multiple processes would each have their own, inconsistent view of who's
connected and would miss each other's broadcasts. This is a v1 constraint,
not a default you're expected to tune - the image's `CMD` always starts a
single worker.

## TLS / HTTPS

The image never terminates TLS itself; it only ever speaks HTTP internally.
HTTPS is provided by whatever sits in front of it.

### On a PaaS

Most PaaS providers (Fly.io, Railway, Render, etc.) terminate TLS at their
own load balancer and forward plain HTTP to your container - nothing to
configure in colist itself. Just set `COLIST_CORS_ORIGINS` if needed and
attach a persistent volume/disk mounted at `/data`.

### On a VPS

Put a reverse proxy in front of the container to handle TLS. [Caddy](https://caddyserver.com/)
is the simplest option - it provisions and renews Let's Encrypt certificates
automatically with only a few lines of config.

Example `docker-compose.yml`:

```yaml
services:
  app:
    build: .
    restart: unless-stopped
    volumes:
      - colist-data:/data
    environment:
      COLIST_CORS_ORIGINS: https://your-domain.example
    expose:
      - "8000"

  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy-data:/data
      - caddy-config:/config
    depends_on:
      - app

volumes:
  colist-data:
  caddy-data:
  caddy-config:
```

Example `Caddyfile`:

```
your-domain.example {
    reverse_proxy app:8000
}
```

Caddy automatically sets `X-Forwarded-Proto` on requests it proxies, which
the app trusts via `--proxy-headers` (see `Dockerfile`) to correctly mark
session cookies as `Secure`. Only the `app` service's port is exposed to
Caddy over the internal compose network - port 8000 is never published to
the host/internet directly, so the default `COLIST_FORWARDED_ALLOW_IPS=*`
(trust forwarded headers from any peer that can reach the container) is safe
in this topology. If you ever expose port 8000 directly to untrusted
networks, tighten `COLIST_FORWARDED_ALLOW_IPS` to the proxy's address
instead.