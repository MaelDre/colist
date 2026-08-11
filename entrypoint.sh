#!/bin/sh
set -e

# /data may be a bind-mounted volume (Railway Volumes, a VPS named volume,
# ...) provided by the platform at container start, whose ownership the
# image's build-time `chown` (Dockerfile) cannot affect - a freshly mounted
# volume is commonly owned by root. Fix it here, as root, before dropping
# to the non-root `colist` user to actually run the app.
mkdir -p /data
chown -R colist:colist /data

exec gosu colist "$@"
