import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def request(path, payload=None, base="http://lakekeeper:8181/management/v1/"):
    data = None if payload is None else json.dumps(payload).encode()
    req = Request(
        base + path,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(req, timeout=30) as response:
        body = response.read()
        return json.loads(body) if body else None


def ensure_namespace():
    base = "http://lakekeeper:8181/catalog/v1/"
    config = request("config?warehouse=demo", base=base)
    properties = {**config.get("defaults", {}), **config.get("overrides", {})}
    prefix = properties.get("prefix", "").strip("/")
    endpoint = (prefix + "/" if prefix else "") + "namespaces"
    try:
        request(endpoint, {
            "namespace": ["meetup"],
            "properties": {"location": "s3://warehouse/meetup/data"},
        }, base=base)
    except HTTPError as error:
        if error.code != 409:
            raise


def main():
    try:
        request("bootstrap", {"accept-terms-of-use": True})
    except HTTPError as error:
        if error.code != 409 and (
            error.code != 400
            or json.loads(error.read()).get("error", {}).get("type") != "CatalogAlreadyBootstrapped"
        ):
            raise
    warehouses = request("warehouse?project-id=00000000-0000-0000-0000-000000000000")
    if any(item["name"] == "demo" for item in warehouses["warehouses"]):
        print("Warehouse demo already exists.")
        ensure_namespace()
        return
    request("warehouse", {
        "warehouse-name": "demo",
        "project-id": "00000000-0000-0000-0000-000000000000",
        "storage-profile": {
            "type": "s3",
            "bucket": "warehouse",
            "key-prefix": "meetup",
            "endpoint": "http://silo:9000",
            "region": "local-01",
            "path-style-access": True,
            "flavor": "minio",
            "sts-enabled": True,
        },
        "storage-credential": {
            "type": "s3",
            "credential-type": "access-key",
            "aws-access-key-id": "meetup",
            "aws-secret-access-key": "meetup-storage",
        },
    })
    ensure_namespace()
    print("Lakekeeper bootstrapped; demo warehouse uses Silo and PostgreSQL.")


if __name__ == "__main__":
    main()
