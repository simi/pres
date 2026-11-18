#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

docker compose down --remove-orphans
printf 'Stopped. PostgreSQL files remain in pg; start.sh resets them.\n'
