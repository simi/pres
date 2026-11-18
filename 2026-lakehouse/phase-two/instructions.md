# Phase two: Iceberg

localhost:8181
localhost:9001 `meetup` / `meetup-storage`

Shell: `phase-two`

```sh
./start.sh
PGPASSWORD=meetup psql -X -P pager=off -v ON_ERROR_STOP=1 'host=127.0.0.1 port=9005 user=meetup dbname=default sslmode=disable gssencmode=disable'
```

psql:

```sql
SET allow_database_iceberg = 1;
SET allow_insert_into_iceberg = 1;
SET write_full_path_in_iceberg_metadata = 1;

CREATE DATABASE lake
ENGINE = DataLakeCatalog('http://lakekeeper:8181/catalog', 'meetup', 'meetup-storage')
SETTINGS catalog_type = 'rest', warehouse = 'demo',
    aws_access_key_id = 'meetup', aws_secret_access_key = 'meetup-storage',
    storage_endpoint = 'http://silo:9000/warehouse';

CREATE TABLE lake.`meetup.revenues`
(
    customer Nullable(String),
    revenue Nullable(Decimal(12, 2))
)
ENGINE = IcebergS3;
```

- explore lakekeeper (using UI, using PostgreSQL)
  - warehouses
  - namespaces
  - tables (active_tables)
  - columns (schema)

```sh
PGPASSWORD=meetup psql -X -h 127.0.0.1 -p 55435 -U meetup -d catalog
```

```sql
SET allow_database_iceberg = 1;
SET allow_insert_into_iceberg = 1;
SET write_full_path_in_iceberg_metadata = 1;

SHOW TABLES FROM lake;
INSERT INTO lake.`meetup.revenues` VALUES ('Alice', 100.00), ('Bob', 200.00);
SELECT content, file_path, record_count, file_size_in_bytes FROM system.iceberg_files WHERE database = 'lake' AND table = 'meetup.revenues';
SELECT * FROM lake.`meetup.revenues` ORDER BY customer;
SELECT sum(revenue) FROM lake.`meetup.revenues`;


ALTER TABLE lake.`meetup.revenues` UPDATE revenue = 150.00 WHERE customer = 'Alice';
SELECT content, file_path, record_count, file_size_in_bytes FROM system.iceberg_files WHERE database = 'lake' AND table = 'meetup.revenues';
SELECT sum(revenue) FROM lake.`meetup.revenues`;

ALTER TABLE lake.`meetup.revenues` DELETE WHERE customer = 'Bob';
SELECT content, file_path, record_count, file_size_in_bytes FROM system.iceberg_files WHERE database = 'lake' AND table = 'meetup.revenues';

SELECT * FROM lake.`meetup.revenues`;
SELECT sum(revenue) FROM lake.`meetup.revenues`;
SHOW CREATE TABLE lake.`meetup.revenues`;

\q
```

Shell 2: PostgreSQL behind Lakekeeper.

```sh
PGPASSWORD=meetup psql -X -h 127.0.0.1 -p 55435 -U meetup -d catalog
```

psql:

```sql
\d
\q
```

## PyIceberg: read the ClickHouse-written table

Shell: `phase-two`

```sh
uv run iceberg.py
```

Python:

```python
catalog.list_tables("meetup")
table = load_table("meetup.revenues")
table.schema()
rows = table.scan().to_arrow().to_pylist()
rows
sum(row["revenue"] for row in rows)

table.inspect.files().select(                          
    ["file_path", "record_count", "file_size_in_bytes"]
).to_pylist()                                          
```

Python: Ctrl-D. Shell:

```sh
./stop.sh
```
