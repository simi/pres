# Lakehouse + PostgreSQL

Meetup slides and two local demos.

Requirements: Docker with Compose, Python 3.12+, `psql`, `uv`, and `presenterm`.

```sh
presenterm slides-new.md
```

- [Phase one V1](phase-one/v1/instructions.md): PostgreSQL catalog + CSV files + Python reader.
- [Phase one V2](phase-one/v2/instructions.md): table and column metadata in the catalog.
- [Phase two](phase-two/instructions.md): ClickHouse + Lakekeeper + PostgreSQL + Silo, then PyIceberg.

Run commands from the directories named in each guide. `start.sh` resets that demo's generated state; `stop.sh` stops it. The CSVs are fictional sample data and stay in place.

The Compose services use local demo credentials. Generated PostgreSQL files, Silo objects, downloaded Parquet files, and Python environments are excluded from this export.
