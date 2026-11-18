# Phase one V2

Shell: `phase-one/v2`

```sh
python3 -m venv ../../.venv
../../.venv/bin/pip install psycopg2-binary==2.9.13
./start.sh
cat data/sales-2024-01.csv
cat lakehouse.py
psql -X -h 127.0.0.1 -p 55434 -v ON_ERROR_STOP=1 -a
```

psql:

```sql
\i bootstrap.sql
SELECT * FROM catalog_tables;
SELECT * FROM catalog_columns ORDER BY table_name, position;
SELECT * FROM catalog_files ORDER BY table_name, year, month;
\q
```

Shell:

```sh
../../.venv/bin/python lakehouse.py
```

Python:

```python
lake.tables()
lake.from_table("sales").columns()
lake.from_table("sales").where(year=2024, month=1).show()
lake.from_table("sales").where(year=2050, month=1).count()
lake.from_table("sales").group_by("year").sum()
lake.from_table("customers").columns()
lake.from_table("customers").show()
```

Shell 2: same directory.

```sh
psql -X -h 127.0.0.1 -p 55434 -v ON_ERROR_STOP=1
```

psql:

```sql
UPDATE catalog_columns SET name = 'amount'
WHERE table_name = 'sales' AND name = 'revenue';
```

Python:

```python
lake.from_table("sales").columns()
lake.from_table("sales").sum("amount")
```

psql:

```sql
UPDATE catalog_columns SET name = 'revenue'
WHERE table_name = 'sales' AND name = 'amount';
\q
```

Python: Ctrl-D. Shell:

```sh
./stop.sh
```
