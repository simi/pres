#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if [[ -L pg ]]; then
    printf 'Refusing to reset a symlink at pg.\n' >&2
    exit 1
fi

DEMO_UID=$(id -u)
DEMO_GID=$(id -g)
export DEMO_UID DEMO_GID
docker compose down --remove-orphans
printf 'Resetting %s/pg\n' "$PWD"
rm -rf -- pg
mkdir -m 700 pg
docker compose up -d --wait --wait-timeout 60
printf '\nReady: psql -h 127.0.0.1 -p 55434\nBootstrap: psql -X -h 127.0.0.1 -p 55434 -v ON_ERROR_STOP=1 -a -f bootstrap.sql\n'
