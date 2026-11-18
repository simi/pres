BEGIN;

CREATE TABLE sales (
    year integer NOT NULL,
    month integer NOT NULL CHECK (month BETWEEN 1 AND 12),
    path text NOT NULL,
    PRIMARY KEY (year, month)
);

INSERT INTO sales (year, month, path) VALUES
    (2024, 1, 'data/sales-2024-01.csv'),
    (2024, 2, 'data/sales-2024-02.csv'),
    (2024, 3, 'data/sales-2024-03.csv'),
    (2024, 4, 'data/sales-2024-04.csv'),
    (2024, 5, 'data/sales-2024-05.csv'),
    (2024, 6, 'data/sales-2024-06.csv'),
    (2024, 7, 'data/sales-2024-07.csv'),
    (2024, 8, 'data/sales-2024-08.csv'),
    (2024, 9, 'data/sales-2024-09.csv'),
    (2024, 10, 'data/sales-2024-10.csv'),
    (2024, 11, 'data/sales-2024-11.csv'),
    (2024, 12, 'data/sales-2024-12.csv'),
    (2025, 1, 'data/sales-2025-01.csv'),
    (2025, 2, 'data/sales-2025-02.csv'),
    (2025, 3, 'data/sales-2025-03.csv'),
    (2025, 4, 'data/sales-2025-04.csv'),
    (2025, 5, 'data/sales-2025-05.csv'),
    (2025, 6, 'data/sales-2025-06.csv'),
    (2025, 7, 'data/sales-2025-07.csv'),
    (2025, 8, 'data/sales-2025-08.csv'),
    (2025, 9, 'data/sales-2025-09.csv'),
    (2025, 10, 'data/sales-2025-10.csv'),
    (2025, 11, 'data/sales-2025-11.csv'),
    (2025, 12, 'data/sales-2025-12.csv');

COMMIT;
