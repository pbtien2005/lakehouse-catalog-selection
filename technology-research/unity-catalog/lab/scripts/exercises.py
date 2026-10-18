"""Learning exercises; changes are confined to the lab.sales namespace and lab volume."""
import argparse
import json
import os
import time
import urllib.error
import urllib.request

from pyspark.sql import SparkSession

BASE = os.environ.get("UC_URI", "http://uc:8080") + "/api/2.1/unity-catalog"
EXTERNAL = "lab.sales.orders_external"
MANAGED = "lab.sales.orders_managed"
EXTERNAL_PATH = "file:///lab-data/external/orders"


def api(path, body=None):
    request = urllib.request.Request(
        BASE + path,
        data=None if body is None else json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode()
        raise RuntimeError(f"UC HTTP {error.code}: {detail}") from error


def ensure(path, create_path, body):
    # Only create after a confirmed 404; never swallow auth/server errors.
    try:
        request = urllib.request.Request(BASE + path)
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
    return api(create_path, body)


def bootstrap():
    for attempt in range(45):
        try:
            api("/catalogs")
            break
        except (OSError, RuntimeError):
            if attempt == 44:
                raise
            time.sleep(2)
    ensure("/catalogs/lab", "/catalogs", {
        "name": "lab", "comment": "Local UC learning lab",
        "storage_root": "file:///lab-data/managed",
    })
    ensure("/schemas/lab.sales", "/schemas", {
        "name": "sales", "catalog_name": "lab",
        "comment": "External versus catalog-managed Delta",
    })


def inspect(spark):
    for table in (EXTERNAL, MANAGED):
        print(f"\n--- {table}: catalog entry ---", flush=True)
        entry = api("/tables/" + table)
        print(json.dumps({key: entry.get(key) for key in (
            "full_name", "table_id", "table_type", "data_source_format", "storage_location"
        )}, indent=2))
        spark.sql(f"DESCRIBE DETAIL {table}").show(truncate=False)
        spark.sql(f"DESCRIBE HISTORY {table}").show(10, truncate=False)
        spark.sql(f"SELECT * FROM {table} ORDER BY id").show()
    print("\n--- Managed table: Delta API load response ---", flush=True)
    state = api("/delta/v1/catalogs/lab/schemas/sales/tables/orders_managed")
    # Do not print a full API response that could include credentials in future configurations.
    print(json.dumps({key: state.get(key) for key in (
        "latest-table-version", "commits", "etag"
    )}, indent=2))
    print("An empty commits list is normal after backfill; it does not mean there was no commit.")


def verify(spark):
    ext = spark.sql(f"DESCRIBE DETAIL {EXTERNAL}").first().asDict()
    managed = spark.sql(f"DESCRIBE DETAIL {MANAGED}").first().asDict()
    assert "catalogManaged" not in (ext.get("tableFeatures") or []), ext
    assert "catalogManaged" in (managed.get("tableFeatures") or []), managed
    assert api("/tables/" + EXTERNAL)["table_type"] == "EXTERNAL"
    assert api("/tables/" + MANAGED)["table_type"] == "MANAGED"
    for table in (EXTERNAL, MANAGED):
        actual = [(r.id, r.amount) for r in spark.sql(
            f"SELECT id, amount FROM {table} ORDER BY id"
        ).collect()]
        assert actual == [(1, 100), (2, 250)], (table, actual)
    print("PASS: external/managed identities, protocol features and expected rows.", flush=True)


def demo(spark):
    # Safe to re-run: overwrite only these two educational tables, without dropping them.
    spark.sql(f"""CREATE TABLE IF NOT EXISTS {EXTERNAL} (id BIGINT, amount BIGINT)
        USING DELTA LOCATION '{EXTERNAL_PATH}'""")
    spark.sql(f"""CREATE TABLE IF NOT EXISTS {MANAGED} (id BIGINT, amount BIGINT)
        USING DELTA TBLPROPERTIES ('delta.feature.catalogManaged'='supported')""")
    for table in (EXTERNAL, MANAGED):
        spark.sql(f"INSERT OVERWRITE {table} VALUES (1, 100), (2, 200)")
        before = int(spark.sql(f"DESCRIBE HISTORY {table}").first()["version"])
        spark.sql(f"UPDATE {table} SET amount = 250 WHERE id = 2")
        previous = spark.sql(
            f"SELECT amount FROM {table} VERSION AS OF {before} WHERE id=2"
        ).first()["amount"]
        assert previous == 200, (table, previous)
        print(f"PASS: {table}, version {before} still contains amount=200.", flush=True)
    verify(spark)
    inspect(spark)


def snapshot(spark):
    # Delay permits a second terminal to change the table during the observation.
    version = int(spark.sql(f"DESCRIBE HISTORY {MANAGED}").first()["version"])
    before = spark.sql(f"SELECT * FROM {MANAGED} VERSION AS OF {version} ORDER BY id").collect()
    print(f"Snapshot version={version}. Update the table in another terminal within 30 seconds.", flush=True)
    time.sleep(30)
    after = spark.sql(f"SELECT * FROM {MANAGED} VERSION AS OF {version} ORDER BY id").collect()
    assert before == after
    print(f"PASS: pinned snapshot unchanged: {after}", flush=True)
    print("Current table (may differ):", flush=True)
    spark.sql(f"SELECT * FROM {MANAGED} ORDER BY id").show()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["demo", "inspect", "verify", "snapshot"])
    action = parser.parse_args().action
    bootstrap()
    spark = SparkSession.builder.appName("UC-OSS-Learning").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    try:
        {"demo": demo, "inspect": inspect, "verify": verify, "snapshot": snapshot}[action](spark)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
