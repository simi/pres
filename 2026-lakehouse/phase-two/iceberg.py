#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyiceberg[pyarrow]==0.12.0"]
# ///

import code

from pyiceberg.catalog import load_catalog
from pyiceberg.io.pyarrow import PyArrowFileIO


STORAGE = {
    "s3.endpoint": "http://127.0.0.1:19000",
    "s3.access-key-id": "meetup",
    "s3.secret-access-key": "meetup-storage",
    "s3.region": "local-01",
    "s3.force-virtual-addressing": "false",
}

catalog = load_catalog("demo", **{
    "type": "rest",
    "uri": "http://127.0.0.1:8181/catalog",
    "warehouse": "demo",
    "header.X-Iceberg-Access-Delegation": "",
    **STORAGE,
})


def load_table(name="meetup.revenues"):
    table = catalog.load_table(name)
    table.io = PyArrowFileIO({**table.io.properties, **STORAGE})
    return table


if __name__ == "__main__":
    code.interact(
        banner="catalog, load_table() - Ctrl-D to quit",
        local={"catalog": catalog, "load_table": load_table},
    )
