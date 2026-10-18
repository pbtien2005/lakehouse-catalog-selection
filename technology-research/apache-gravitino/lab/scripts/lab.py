"""Small, dependency-free REST client for the Gravitino learning lab."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8090"
ROOT = "/api/metalakes/learning"
PG = ROOT + "/catalogs/pg_shop"
FILES = ROOT + "/catalogs/lake_files/schemas/landing/filesets"


def redact(value):
    if isinstance(value, dict):
        return {k: "***" if any(s in k.lower() for s in ("password", "secret", "token"))
                else redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


def request(method, path, body=None):
    if not path.startswith("/api/") or ".." in path:
        raise ValueError("Use an absolute /api/... path on this lab's Gravitino server")
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = Request(BASE + path, data=data, method=method, headers={
        "Accept": "application/vnd.gravitino.v1+json",
        "Content-Type": "application/json",
    })
    with urlopen(req, timeout=15) as response:
        result = json.load(response)
    if result.get("code", 0) != 0:
        raise RuntimeError(f"API returned nonzero code: {redact(result)}")
    return result


def check(condition, message):
    if not condition:
        raise RuntimeError(message)
    print("PASS: " + message)


def ensure(collection, body):
    path = collection + "/" + body["name"]
    try:
        result = request("GET", path)
        print("EXISTS: " + path)
        return result
    except HTTPError as error:
        if error.code != 404:
            raise
    result = request("POST", collection, body)
    print("CREATED: " + path)
    return result


def wait_ready():
    for _ in range(90):
        try:
            result = request("GET", "/api/health/ready")
            if str(result.get("status", "")).lower() == "up":
                return
        except (HTTPError, URLError, TimeoutError):
            pass
        time.sleep(2)
    raise RuntimeError("Gravitino not ready after 180s; inspect docker compose logs")


def bootstrap():
    wait_ready()
    password = os.environ.get("LAB_POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError("LAB_POSTGRES_PASSWORD is missing; run inside the gravitino container")
    ensure("/api/metalakes", {"name": "learning", "comment": "Gravitino learning lab", "properties": {}})
    ensure(ROOT + "/catalogs", {
        "name": "pg_shop", "type": "RELATIONAL", "provider": "jdbc-postgresql",
        "comment": "Existing operational PostgreSQL database",
        "properties": {
            "jdbc-url": "jdbc:postgresql://postgres:5432/shop?connectTimeout=5&socketTimeout=10",
            "jdbc-driver": "org.postgresql.Driver", "jdbc-database": "shop",
            "jdbc-user": "lab", "jdbc-password": password,
            "jdbc.pool.min-size": "1", "jdbc.pool.max-size": "4", "jdbc.pool.max-wait-ms": "5000",
        },
    })
    ensure(ROOT + "/catalogs", {
        "name": "lake_files", "type": "FILESET", "provider": "fileset",
        "comment": "Non-tabular assets on a local Docker volume",
        "properties": {"location": "file:///raw-files/managed"},
    })
    ensure(ROOT + "/catalogs/lake_files/schemas", {
        "name": "landing", "comment": "Incoming files", "properties": {},
    })
    ensure(FILES, {
        "name": "incoming_events", "type": "EXTERNAL", "comment": "Existing JSONL files",
        "storageLocation": "file:///raw-files/external/incoming", "properties": {},
    })
    print("PASS: bootstrap complete; existing objects and source data were retained")


def table_body(name):
    return {
        "name": name, "comment": "Table created through the Gravitino PostgreSQL provider",
        "columns": [
            {"name": "id", "type": "long", "nullable": False, "comment": "Event identifier"},
            {"name": "note", "type": "string", "nullable": True, "comment": "Observation"},
        ],
        "properties": {},
    }


def smoke_create(name):
    tables = request("GET", PG + "/schemas/sales/tables")
    names = [t["name"] for t in tables["identifiers"]]
    check("orders" in names and "customers" in names, "existing PostgreSQL tables discovered")
    request("POST", PG + "/schemas/sales/tables", table_body(name))
    check(request("GET", PG + "/schemas/sales/tables/" + name)["table"]["name"] == name,
          "DDL through Gravitino created the test table")


def smoke_verify(name):
    table = request("GET", PG + "/schemas/sales/tables/" + name)["table"]
    check("native_column" in [c["name"] for c in table["columns"]],
          "native PostgreSQL ALTER is visible through Gravitino")
    tag = "tag_" + name
    request("POST", ROOT + "/tags", {"name": tag, "comment": "Smoke classification", "properties": {}})
    obj = ROOT + "/objects/table/pg_shop.sales." + name + "/tags"
    request("POST", obj, {"tagsToAdd": [tag], "tagsToRemove": []})
    check(tag in request("GET", obj)["names"], "tag associated with a federated table")

    # Use disposable directories isolated from the learner's sample fileset.
    for kind in ("MANAGED", "EXTERNAL"):
        fs_name = name + "_" + kind.lower()
        directory = Path("/raw-files/smoke") / fs_name
        directory.mkdir(parents=True)
        marker = directory / "marker.txt"
        marker.write_text("storage lifecycle check\n", encoding="utf-8")
        request("POST", FILES, {
            "name": fs_name, "type": kind, "comment": "Disposable smoke fileset",
            "storageLocation": directory.as_uri(), "properties": {},
        })
        check(request("GET", FILES + "/" + fs_name)["fileset"]["type"].upper() == kind,
              kind + " fileset registered")
        request("DELETE", FILES + "/" + fs_name)
        if kind == "EXTERNAL":
            check(marker.exists(), "EXTERNAL drop preserves physical files")
            marker.unlink()
            directory.rmdir()
        else:
            check(not directory.exists(), "MANAGED drop removes its physical directory")
    request("DELETE", ROOT + "/tags/" + tag)
    request("DELETE", PG + "/schemas/sales/tables/" + name)
    check(Path("/raw-files/external/incoming/events.jsonl").is_file(), "learner's sample file retained")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("health", "wait", "bootstrap"):
        sub.add_parser(command)
    api = sub.add_parser("api")
    api.add_argument("method", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    api.add_argument("path")
    api.add_argument("body_file", nargs="?")
    for command in ("smoke-create", "smoke-verify"):
        smoke = sub.add_parser(command)
        smoke.add_argument("name")
    args = parser.parse_args()
    if args.command == "health":
        if str(request("GET", "/api/health/ready").get("status", "")).lower() != "up":
            raise RuntimeError("Entity store is not ready")
    elif args.command == "wait":
        wait_ready()
    elif args.command == "bootstrap":
        bootstrap()
    elif args.command == "api":
        body = json.loads(Path(args.body_file).read_text(encoding="utf-8-sig")) if args.body_file else None
        print(json.dumps(redact(request(args.method, args.path, body)), indent=2, ensure_ascii=False))
    else:
        if not re.fullmatch(r"smoke_[a-f0-9]{12}", args.name):
            raise ValueError("Smoke object name must match smoke_[a-f0-9]{12}")
        (smoke_create if args.command == "smoke-create" else smoke_verify)(args.name)


if __name__ == "__main__":
    try:
        main()
    except HTTPError as error:
        # Do not print request bodies or backend exception messages containing credentials.
        try:
            detail = json.loads(error.read()).get("type", "HTTPError")
        except (ValueError, AttributeError):
            detail = "HTTPError"
        print(f"FAIL: HTTP {error.code}, {detail}. Check server logs for details.", file=sys.stderr)
        sys.exit(1)
    except (URLError, OSError, RuntimeError, ValueError, KeyError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
