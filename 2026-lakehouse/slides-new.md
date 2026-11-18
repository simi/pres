---
title: Lakehouse + PostgreSQL
sub_title: Catalog, storage, reader
author: Josef Šimánek
---

# 0. Introduction

What would be covered?

- What is Lakehouse and little background
- How to implement Lakehouse from scratch using PostgreSQL
- How to use existing Lakehouse implementation with PostgreSQL

**Announcement**: It will be heavily simplified for the sake of presentation time constraints.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What will we leave out?</span>

<!-- end_slide -->

# 0. Introduction

What would not be (mostly) covered?

- How to implement Lakehouse solely using PostgreSQL
- PostgreSQL extensions
- DuckDB demo (everyone is tired of DuckDB, or just me?)

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What is the agenda?</span>

<!-- end_slide -->

# 0. Agenda

- Goal? Understand the Lakehouse data architecture pattern basics.
- A little theory
- A lot of demo
- Summary and recommendations

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Which terms do we need?</span>

<!-- end_slide -->

# 1. Terminology (high level)

- data architecture patterns
- 1/2 Warehouse + 1/2 Data lake ~= Lakehouse
- What is Warehouse?
- What is Data lake?

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What is a warehouse?</span>

<!-- end_slide -->

# 1.1 Warehouse

- sometimes Data Warehouse
- Prepared, structured historical data. Built for analytical questions.
- IBM (1988): bring operational data together for analysis.

Paper: *An architecture for a business
and information system*, IBM Systems Journal.

Sources:

- The Data Warehouse Toolkit by Ralph Kimball (John Wiley and Sons, 1996)
- Building the Data Warehouse by William Inmon (John Wiley and Sons, 1996)
- [Devlin and Murphy, 1988](https://doi.org/10.1147/sj.271.0060)

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Have you seen these data patterns?</span>

<!-- end_slide -->

# 1.1 Warehouse

Have you seen those data patterns:

- Mostly appending.
- Time-based data, sales, retained history.
- Non-transactional (transactional -> non-transactional)
- ~OLAP

*Signs, not a checklist.*

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What is a data lake?</span>

<!-- end_slide -->

# 1.2 Data lake

- Raw or archived data from different sources.
- Kept together, in native formats for future "questions".
- CSV, JSON, logs, images, proprietary files...
- Object storage is common (S3, GCS, ABS).
- A local directory of random data files.

Sources:

- [AWS data lake definition](https://aws.amazon.com/what-is/data-lake/)
- [James Dixon's blog](https://jamesdixon.wordpress.com/2010/10/14/pentaho-hadoop-and-data-lakes/)

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What does a data lake look like?</span>

<!-- end_slide -->

# 1.2. A data lake can look like this

```text
s3://data-lake/
├── sales/
│   ├── sales-2024.csv
│   └── sales-2025.parquet
├── people/
│   └── contractors.xlsx
└── logs/
    └── app-2025-01.log
```

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What does a lakehouse add?</span>

<!-- end_slide -->

# 1.3. Lakehouse

The middle ground.

Warehouse-style tables and transactions
over open lake storage.

Source: [Armbrust et al., CIDR 2021](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf) by Databricks

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What are the pieces?</span>

<!-- end_slide -->

# 1.3. Lakehouse pieces

- **Catalog** - what is there?
- **Storage** - where is it?
- **Reader** and **Writer** - how do we work with it?

Those are usually bundled together (like in PostgreSQL).
In Lakehouse could be separate.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: How does PostgreSQL fit in?</span>

<!-- end_slide -->

# 2. Terminology + PostgreSQL

The same terms, now through PostgreSQL eyes.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Could PostgreSQL be a warehouse?</span>

<!-- end_slide -->

# 2.1. Could PostgreSQL be a warehouse?

Yes, PostgreSQL can host a data warehouse.

Have you seen those data patterns:

- Long-lived tables with historical data.
- Mostly appending, often time-based.
- Old data treated as read-only by business logic.
- Reporting, long scans and aggregations.

*Signs, not a checklist.*

Read-only history is often an application rule,
not something PostgreSQL enforces automatically.

There is no special warehouse mode. Keep doing what you do.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Could PostgreSQL be a data lake?</span>

<!-- end_slide -->

# 2.2. Could PostgreSQL be a data lake?

Usually no.

You could store random files as blobs inside the database.

I hope that's rare. There are better places to keep those files.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Could PostgreSQL be a lakehouse?</span>

<!-- end_slide -->

# 2.3. Could PostgreSQL be a lakehouse?

**???**

Let's find out.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What do we need to build one?</span>

<!-- end_slide -->

# 3. Mysterious Lakehouse

What do we need to build one?

- **Catalog** - what tables, columns and files exist?
- **Storage** - where is the data?
- **Readers and writers** - how do we access it?

Common database building blocks. PostgreSQL has them too.

Let's look at plain PostgreSQL first.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Where are those pieces in PostgreSQL?</span>

<!-- end_slide -->

# 3.1. The pieces in plain PostgreSQL

- **Catalog** - `pg_class`, `pg_attribute`, other system tables.
- **Storage** - files in the data directory.
- **Readers and writers** - table/index access methods, `pg_am`.

```sql
SELECT relname FROM pg_class LIMIT 5;
SHOW data_directory;
SELECT pg_relation_filepath('pg_class');
SELECT amname, amtype FROM pg_am;
```

File path is relative to the data directory.
`amtype`: `t` = table, `i` = index. Default table method: `heap`.

Sources: PostgreSQL 17 docs - System Catalogs,
Database File Layout, Table Access Method Interface.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: How do these pieces work together?</span>

<!-- end_slide -->

# 3.2. Reading

1. Reader asks the catalog where to find the data.
2. Catalog returns storage locations.
3. Reader reads the data from those locations.

```text
Reader -> Catalog: where is the data?
Reader -> Storage: read the data
```

The catalog tells us where. Storage holds the data.

Catalog reads need a consistent, committed state.
No catalog transaction needs to stay open while reading files.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What changes when we write?</span>

<!-- end_slide -->

# 3.2. Writing

1. Writer asks the catalog where the data belongs.
2. Writer writes the data to storage.
3. Writer updates the catalog when needed.

```text
Writer -> Catalog: where does the data belong?
Writer -> Storage: write the data
Writer -> Catalog: update its description
```

Same pieces, now changing the data.

Catalog changes must commit atomically (all or nothing).
The catalog transaction does not include writing the files.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Can we build a simple version?</span>

<!-- end_slide -->

# 3.3. Demo V1: build our own

- **Catalog + its transactions** - PostgreSQL can do that.
- **Storage** - a local folder with CSV files.
- **Reader** - our own simple Python script, `lakehouse.py`.

A few lines to ask the catalog, find the files and read the data.

Our oversimplified lakehouse. Let's try it.

Demo: `phase-one/v1`.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What is wrong with this version?</span>

<!-- end_slide -->

# 3.3. Demo V1: what is missing?

- **Transactions** - PostgreSQL protects the catalog, not our CSV operations.
- **Exposed storage** - anyone with file access can bypass the catalog and reader.
- **Hardcoded schema** - no CSV headers; `lakehouse.py` must know the column order and types.

Simplified on purpose. Hardcoded, inflexible, not dynamic.

How do we protect the data folder?
How do we teach the lakehouse about the CSV structure?

We will move the schema into the catalog in V2.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Can we make it a little more dynamic?</span>

<!-- end_slide -->

# 3.4. Demo V2: a little more dynamic

Add tables and columns to the catalog.

The reader asks for column order, names and types.
Same reader, different CSV structures.

Still simple. Just a little less hardcoded.

Demo: `phase-one/v2`.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What would V3 look like?</span>

<!-- end_slide -->

# 3.5. Demo V3: no demo, just imagine

We could keep going:

- Schema changes and migrations.
- Coordinate catalog changes and file writes.
- More formats, types and features.

The schema is in PostgreSQL now. A useful starting point.

Each step makes it more dynamic, secure and generic.
We are heading towards a reusable lakehouse system.

For this demo, we stop here.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Has someone already done this?</span>

<!-- end_slide -->

# 4. Iceberg and friends

Probably not worth building all of this from scratch.

Smarter people have already done the work.

There are specifications defining the rules,
and implementations following those specifications.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Which open table formats are out there?</span>

<!-- end_slide -->

# 4.1. Open table formats

- **Delta Lake** - batch + streaming.
- **Apache Hudi** - efficient upserts.
- **Apache Iceberg** - partition evolution.

Sources: Delta Lake documentation; Apache Hudi Overview;
Apache Iceberg Evolution.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Let's look at Iceberg.</span>

<!-- end_slide -->

# 4.2. Apache Iceberg

Created at Netflix by Ryan Blue and Daniel Weeks.

- **2018** - publicly presented; joined the Apache Incubator.
- **2020** - became an Apache top-level project.

Who implements support for it?

- **Engines** - Spark, Flink, Trino, ClickHouse.
- **Python** - PyIceberg.
- **Catalog** - Lakekeeper, backed by PostgreSQL.

Sources: Strata NY 2018 talks; Apache Iceberg board history;
Apache Iceberg integrations; Lakekeeper documentation.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What will our Iceberg demo run?</span>

<!-- end_slide -->

# 4.3. Demo: Iceberg

- **Lakekeeper** - implements the Iceberg REST catalog.
- **PostgreSQL** - stores Lakekeeper's catalog state.
- **Silo** - local S3-compatible storage, backed by disk.
- **ClickHouse** - our reader and writer for Iceberg tables.

```text
ClickHouse -> Lakekeeper -> PostgreSQL
    |
    +------> Silo -> local disk
```

ClickHouse uses the catalog and reads/writes files in Silo.
Silo holds Iceberg metadata files and the actual data files.

Object storage is usually S3, GCS or Azure Blob Storage.
Here we use Silo to keep the demo local.

Demo: `phase-two`.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Can another reader use the same tables?</span>

<!-- end_slide -->

# 4.4. Demo: PyIceberg

Same Iceberg tables. Same catalog. Same files.
Another reader: PyIceberg instead of ClickHouse.

```text
PyIceberg -> Lakekeeper -> PostgreSQL
    |
    +-----> Silo -> local disk
```

Choose compatible components to fit your needs.
Each has different features, limits and deployment requirements.

Demo: `phase-two`, run `uv run iceberg.py`.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What else is worth watching?</span>

<!-- end_slide -->

# 4.5. DuckLake: worth a look

Iceberg is a leading open table format.
DuckLake is a newer approach, introduced in May 2025.

- All metadata in a SQL database, including PostgreSQL.
- Data in Parquet files, locally or in object storage.

No demo. Let's take a look at [ducklake.select](https://ducklake.select/).

Sources: Riso Group, Data Platform Adoption (July 2026);
DuckLake announcement (May 2025), DuckLake website.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Who cleans up after all those writes?</span>

<!-- end_slide -->

# 4.6. Maintenance

Cleanup is similar in purpose to PostgreSQL VACUUM.

- **DELETE / UPDATE** - may mark rows or rewrite files.
- **Compaction** - merge small files, apply pending deletes.
- **Expire history** - give up old snapshots / time travel.
- **Cleanup** - physically remove files no longer needed.

Compaction alone does not remove history.
Keep files needed by retained history and active readers.

Example: merge A + B into C. An old reader may still need A.
Delete A too soon and that reader can fail.

Follow your format and engine's maintenance guidance.
Schedule jobs and choose retention accordingly.

Sources: Apache Iceberg Maintenance; DuckLake Cleanup of Files;
PostgreSQL Routine Vacuuming.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Could we do it solely in PostgreSQL?</span>

<!-- end_slide -->

# 5.1. A lakehouse solely in PostgreSQL?

In theory, yes. There are pieces to build on.

**pg_parquet** by Crunchy Data:

- Read and write Parquet via `COPY TO/FROM`.
- Local files, S3, GCS and Azure Blob Storage.
- A useful building block; not a complete lakehouse.

[CrunchyData/pg_parquet](https://github.com/CrunchyData/pg_parquet)

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What about pg_lake?</span>

<!-- end_slide -->

# 5.2. pg_lake

PostgreSQL extensions for Iceberg and data lake access.

Uses DuckDB through a separate `pgduck_server` process.
DuckDB is not embedded inside the PostgreSQL process.

```text
PostgreSQL + pg_lake -> pgduck_server (DuckDB)
```

Still another engine, so not PostgreSQL-only execution.
My preference: keep extra engines outside PostgreSQL.

[Snowflake-Labs/pg_lake](https://github.com/Snowflake-Labs/pg_lake)

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Can foreign data wrappers help?</span>

<!-- end_slide -->

# 5.3. Foreign data wrappers

Query external data through foreign tables.

- **[file_fdw](https://www.postgresql.org/docs/current/file-fdw.html)** - ships with PostgreSQL; local CSV / text, read-only.
- **[parquet_fdw](https://github.com/adjust/parquet_fdw)** - local Parquet, read-only.
- **[parquet_s3_fdw](https://github.com/pgspider/parquet_s3_fdw)** - local / S3 Parquet, reads and writes.
- **[www_fdw](https://github.com/cyga/www_fdw)** - HTTP services; original project unmaintained.

Parquet access alone does not give us Iceberg semantics.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: What about PostgreSQL core?</span>

<!-- end_slide -->

# 5.4. PostgreSQL core

Not a new idea. There is progress.

- **2018** - Avro / Parquet / ORC discussion: make COPY extensible.
- **2019** - table access methods shipped in PostgreSQL 12.
- **2022** - Cloud-friendly COPY: formats + S3 / GCS / HTTP transports.
- **Today** - extensible COPY still under review, not shipped.

Core provides building blocks. Full lakehouse integrations
are currently extensions and external components.

Sources: pgsql-general (2018); PostgreSQL 12 release notes;
Hannu Krosing, Cloud-friendly COPY;
[CommitFest #4681](https://commitfest.postgresql.org/patch/4681/).

Status checked: 30 October 2026.

<!-- new_line -->

<!-- alignment: right -->

<span style="color: #888888">Next: Questions?</span>

<!-- end_slide -->

# Thank you!

Questions?

<!-- end_slide -->
