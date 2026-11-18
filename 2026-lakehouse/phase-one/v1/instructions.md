# Phase one V1

Shell: `phase-one/v1`

```sh
python3 -m venv ../../.venv
../../.venv/bin/pip install psycopg2-binary==2.9.13
./start.sh
cat data/sales-2024-01.csv
cat lakehouse.py
psql -X -h 127.0.0.1 -p 55432 -v ON_ERROR_STOP=1 -a
```

psql:

```sql
\i bootstrap.sql
SELECT * FROM sales ORDER BY year, month;
\q
```

Shell:

```sh
../../.venv/bin/python lakehouse.py
```

Python:

```python
sales = lake.from_table("sales")
sales.count()
sales.where(year=2024, month=1).show()
sales.where(year=2024, month=1).sum()
sales.where(year=2050, month=1).count()
sales.group_by("year").sum()
```

Manually change a revenue in `data/sales-2024-01.csv`.

Python:

```python
sales.where(year=2024, month=1).sum()
```

Restore the CSV. Shell 2: same directory.

```sh
psql -X -h 127.0.0.1 -p 55432
```

psql: prepare the table and note its file path.

```sql
CREATE TABLE file_demo (value text) WITH (autovacuum_enabled = false);
INSERT INTO file_demo VALUES ('MEETUP_REVENUE_100.00');
SELECT pg_relation_filepath('file_demo');
\q
```

Shell 2: restart once to clear shared buffers, then reconnect.

```sh
docker compose restart postgres
psql -X -h 127.0.0.1 -p 55432
```

psql: do not select the table yet.

```sql
BEGIN;
```

Manually replace `MEETUP_REVENUE_100.00` with `MEETUP_REVENUE_900.00` in `pg/<printed path>`, keeping the same byte length.

psql:

```sql
SELECT value FROM file_demo;
ROLLBACK;
SELECT value FROM file_demo;
DROP TABLE file_demo;
\q
```

Cached pages can hide disk edits. Keep other clients from reading this table before the edit.

Python: Ctrl-D. Shell:

```sh
./stop.sh
```
