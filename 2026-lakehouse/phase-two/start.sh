#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if [[ -L silo ]]; then
    printf 'Refusing to reset a symlink at silo.\n' >&2
    exit 1
fi

DEMO_UID=$(id -u)
DEMO_GID=$(id -g)
export DEMO_UID DEMO_GID
docker compose down --volumes --remove-orphans
rm -rf -- silo
mkdir -m 700 silo
docker compose up --build -d --wait --wait-timeout 180
cat <<'EOF'

ClickHouse:
PGPASSWORD=meetup psql -X 'host=127.0.0.1 port=9005 user=meetup dbname=default sslmode=disable gssencmode=disable'

PostgreSQL behind Lakekeeper:
PGPASSWORD=meetup psql -X -h 127.0.0.1 -p 55435 -U meetup -d catalog
EOF
