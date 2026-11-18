import code
import csv
import sys
from collections import defaultdict
from contextlib import closing
from datetime import date
from decimal import Decimal

import psycopg2
from psycopg2 import sql


SCHEMA = (
    ("date", date.fromisoformat),
    ("customer", str),
    ("revenue", Decimal),
)


class Catalog:
    def query(self, statement, params=()):
        with closing(psycopg2.connect("host=127.0.0.1 port=55432")) as connection, connection.cursor() as cursor:
            print("SQL:", cursor.mogrify(statement, params).decode(), file=sys.stderr, flush=True)
            cursor.execute(statement, params)
            return cursor.fetchall()

    def prune_partitions(self, table, predicates):
        statement = sql.SQL("SELECT path FROM {} WHERE true").format(sql.Identifier(table))
        params = []
        for key, value in predicates:
            if key in ("year", "month"):
                statement += sql.SQL(" AND {} = %s").format(sql.Identifier(key))
                params.append(value)
        statement += sql.SQL(" ORDER BY year, month")
        return [path for (path,) in self.query(statement, params)]


catalog = Catalog()


def read_csv(path, schema):
    with open(path, newline="") as file:
        print("OPEN:", path, file=sys.stderr, flush=True)
        for values in csv.reader(file):
            row = {name: parse(value) for (name, parse), value in zip(schema, values, strict=True)}
            row.update(year=row["date"].year, month=row["date"].month)
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

    def rows(self):
        for path in catalog.prune_partitions(self.table, self.predicates):
            for row in read_csv(path, SCHEMA):
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
