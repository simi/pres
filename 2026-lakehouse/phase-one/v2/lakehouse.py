import code
import csv
import sys
from collections import defaultdict
from contextlib import closing
from datetime import date
from decimal import Decimal

import psycopg2
from psycopg2 import sql


TYPES = {"date": date.fromisoformat, "text": str, "integer": int, "decimal": Decimal}


class Catalog:
    def query(self, statement, params=()):
        with closing(psycopg2.connect("host=127.0.0.1 port=55434")) as connection, connection.cursor() as cursor:
            print("SQL:", cursor.mogrify(statement, params).decode(), file=sys.stderr, flush=True)
            cursor.execute(statement, params)
            return cursor.fetchall()

    def tables(self):
        return [name for (name,) in self.query("SELECT name FROM catalog_tables ORDER BY name")]

    def columns(self, table):
        return self.query("SELECT name, type FROM catalog_columns WHERE table_name = %s ORDER BY position", (table,))

    def prune_partitions(self, table, predicates, columns):
        partition_columns = set()
        if ("date", "date") in columns:
            partition_columns = {"year", "month"} - {name for name, kind in columns}
        statement = sql.SQL("SELECT path FROM catalog_files WHERE table_name = %s")
        params = [table]
        for key, value in predicates:
            if key in partition_columns:
                statement += sql.SQL(" AND {} = %s").format(sql.Identifier(key))
                params.append(value)
        statement += sql.SQL(" ORDER BY year, month")
        return [path for (path,) in self.query(statement, params)]


catalog = Catalog()


def read_csv(path, columns):
    with open(path, newline="") as file:
        print("OPEN:", path, file=sys.stderr, flush=True)
        for values in csv.reader(file):
            row = {name: TYPES[kind](value) for (name, kind), value in zip(columns, values, strict=True)}
            if isinstance(row.get("date"), date):
                row.setdefault("year", row["date"].year)
                row.setdefault("month", row["date"].month)
            yield row


class Lakehouse:
    def __init__(self, table=None, predicates=(), grouping=None):
        self.table = table
        self.predicates = predicates
        self.grouping = grouping

    def from_table(self, table):
        return Lakehouse(table)

    def where(self, **predicates):
        return Lakehouse(self.table, self.predicates + tuple(predicates.items()), self.grouping)

    def group_by(self, column):
        return Lakehouse(self.table, self.predicates, column)

    def tables(self):
        return catalog.tables()

    def columns(self):
        return catalog.columns(self.table)

    def rows(self):
        columns = self.columns()
        if not columns:
            raise ValueError(f"No columns for table {self.table}")
        for path in catalog.prune_partitions(self.table, self.predicates, columns):
            for row in read_csv(path, columns):
                if all(row[key] == value for key, value in self.predicates):
                    yield row

    def all(self):
        return list(self.rows())

    def show(self):
        for row in self.rows():
            print(row)

    def count(self):
        return sum(1 for row in self.rows())

    def sum(self, column="revenue"):
        if self.grouping is None:
            return sum((row[column] for row in self.rows()), Decimal(0))
        totals = defaultdict(Decimal)
        for row in self.rows():
            totals[row[self.grouping]] += row[column]
        return dict(totals)


if __name__ == "__main__":
    code.interact(
        banner="lake.from_table('sales') - Ctrl-D to quit",
        local={"lake": Lakehouse(), "catalog": catalog, "date": date},
    )
