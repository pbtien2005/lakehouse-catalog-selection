#!/usr/bin/env bash
set -euo pipefail

# UC 0.6.0 release matrix: Spark 4.0.x + Scala 2.13 + Delta 4.4.0.
args=(
  --master 'local[2]'
  --driver-memory 2g
  --packages 'io.delta:delta-spark_4.0_2.13:4.4.0,io.unitycatalog:unitycatalog-spark_4.0_2.13:0.6.0'
  --conf 'spark.jars.ivy=/tmp/uc-lab-ivy'
  --conf 'spark.jars.ivySettings=/lab/conf/ivysettings.xml'
  --conf 'spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension'
  --conf 'spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog'
  --conf 'spark.sql.catalog.lab=io.unitycatalog.spark.UCSingleCatalog'
  --conf "spark.sql.catalog.lab.uri=${UC_URI:-http://uc:8080}"
  --conf 'spark.sql.catalog.lab.token='
  --conf 'spark.sql.defaultCatalog=lab'
  --conf 'spark.sql.shuffle.partitions=2'
  --conf 'spark.sql.warehouse.dir=/lab-data/spark-warehouse'
  --conf 'spark.ui.enabled=false'
)

if [[ "${1:-demo}" == "shell" ]]; then
  exec /opt/spark/bin/spark-sql "${args[@]}"
fi
exec /opt/spark/bin/spark-submit "${args[@]}" /lab/scripts/exercises.py "${@:-demo}"
