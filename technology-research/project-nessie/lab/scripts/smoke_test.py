"""End-to-end lab check; each run uses its own namespace and branch."""
from uuid import uuid4
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName('nessie-lab-smoke').getOrCreate()
spark.sparkContext.setLogLevel('WARN')
suffix = uuid4().hex[:10]
namespace = f'smoke_{suffix}'
branch = f'dev_{suffix}'
tag = f'verified_{suffix}'
table = f'nessie.{namespace}.orders'

try:
    spark.sql('USE REFERENCE main IN nessie').collect()
    spark.sql(f'CREATE NAMESPACE nessie.{namespace}')
    spark.sql(f'CREATE TABLE {table} (order_id BIGINT, amount DECIMAL(12,2)) USING iceberg')
    spark.sql(f'INSERT INTO {table} VALUES (1, 100.00), (2, 250.00)')
    assert spark.table(table).count() == 2
    spark.sql(f'CREATE BRANCH {branch} IN nessie FROM main').collect()
    spark.sql(f'USE REFERENCE {branch} IN nessie').collect()
    spark.sql(f'INSERT INTO {table} VALUES (3, 75.00)')
    assert spark.table(table).count() == 3
    spark.sql('USE REFERENCE main IN nessie').collect()
    spark.catalog.refreshTable(table)
    assert spark.table(table).count() == 2, 'Branch write leaked into main'
    spark.sql(f'MERGE BRANCH {branch} INTO main IN nessie').collect()
    spark.catalog.refreshTable(table)
    assert spark.table(table).count() == 3, 'Merge did not publish branch data'
    spark.sql(f'CREATE TAG {tag} IN nessie FROM main').collect()
    spark.table(table).orderBy('order_id').show()
    print(f'PASS: create/read/write, branch isolation, merge, tag. Table={table} Branch={branch} Tag={tag}', flush=True)
finally:
    spark.stop()
