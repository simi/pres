BEGIN;

CREATE TABLE catalog_tables (
    name text PRIMARY KEY
);

CREATE TABLE catalog_columns (
    table_name text NOT NULL REFERENCES catalog_tables (name),
    position integer NOT NULL CHECK (position > 0),
    name text NOT NULL,
    type text NOT NULL CHECK (type IN ('date', 'text', 'integer', 'decimal')),
    PRIMARY KEY (table_name, position),
    UNIQUE (table_name, name)
);

CREATE TABLE catalog_files (
    table_name text NOT NULL REFERENCES catalog_tables (name),
    year integer NOT NULL,
    month integer NOT NULL CHECK (month BETWEEN 1 AND 12),
    path text NOT NULL,
    PRIMARY KEY (table_name, year, month)
);

INSERT INTO catalog_tables VALUES ('sales'), ('customers');

INSERT INTO catalog_columns (table_name, position, name, type) VALUES
    ('sales', 1, 'date', 'date'),
    ('sales', 2, 'customer', 'text'),
    ('sales', 3, 'revenue', 'decimal'),
    ('customers', 1, 'id', 'integer'),
    ('customers', 2, 'name', 'text');

INSERT INTO catalog_files (table_name, year, month, path) VALUES
    ('sales', 2024, 1, 'data/sales-2024-01.csv'),
    ('sales', 2024, 2, 'data/sales-2024-02.csv'),
    ('sales', 2024, 3, 'data/sales-2024-03.csv'),
    ('sales', 2024, 4, 'data/sales-2024-04.csv'),
    ('sales', 2024, 5, 'data/sales-2024-05.csv'),
    ('sales', 2024, 6, 'data/sales-2024-06.csv'),
    ('sales', 2024, 7, 'data/sales-2024-07.csv'),
    ('sales', 2024, 8, 'data/sales-2024-08.csv'),
    ('sales', 2024, 9, 'data/sales-2024-09.csv'),
    ('sales', 2024, 10, 'data/sales-2024-10.csv'),
    ('sales', 2024, 11, 'data/sales-2024-11.csv'),
    ('sales', 2024, 12, 'data/sales-2024-12.csv'),
    ('sales', 2025, 1, 'data/sales-2025-01.csv'),
    ('sales', 2025, 2, 'data/sales-2025-02.csv'),
    ('sales', 2025, 3, 'data/sales-2025-03.csv'),
    ('sales', 2025, 4, 'data/sales-2025-04.csv'),
    ('sales', 2025, 5, 'data/sales-2025-05.csv'),
    ('sales', 2025, 6, 'data/sales-2025-06.csv'),
    ('sales', 2025, 7, 'data/sales-2025-07.csv'),
    ('sales', 2025, 8, 'data/sales-2025-08.csv'),
    ('sales', 2025, 9, 'data/sales-2025-09.csv'),
    ('sales', 2025, 10, 'data/sales-2025-10.csv'),
    ('sales', 2025, 11, 'data/sales-2025-11.csv'),
    ('sales', 2025, 12, 'data/sales-2025-12.csv'),
    ('customers', 2024, 1, 'data/customers.csv');

COMMIT;
