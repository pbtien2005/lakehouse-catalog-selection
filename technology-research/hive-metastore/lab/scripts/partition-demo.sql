-- Dedicated demo table. CREATE intentionally fails if the table already exists.
CREATE DATABASE IF NOT EXISTS partition_lab LOCATION 's3a://warehouse/partition_lab.db';

CREATE EXTERNAL TABLE partition_lab.orders_by_day (
  order_id BIGINT,
  amount DECIMAL(10,2)
)
PARTITIONED BY (order_date STRING)
STORED AS PARQUET
LOCATION 's3a://warehouse/partition_lab.db/orders_by_day'
TBLPROPERTIES ('external.table.purge'='false');

-- Spark writes files and registers each static partition with HMS.
INSERT INTO partition_lab.orders_by_day PARTITION (order_date='2026-09-20')
VALUES (1, 100.00), (2, 250.00);
INSERT INTO partition_lab.orders_by_day PARTITION (order_date='2026-09-21')
VALUES (3, 80.00), (4, 120.00);

SHOW PARTITIONS partition_lab.orders_by_day;
SELECT order_date, COUNT(*) AS row_count, SUM(amount) AS total_amount
FROM partition_lab.orders_by_day GROUP BY order_date ORDER BY order_date;

DESCRIBE FORMATTED partition_lab.orders_by_day PARTITION (order_date='2026-09-20');
EXPLAIN FORMATTED SELECT * FROM partition_lab.orders_by_day WHERE order_date='2026-09-20';

-- Register one empty partition explicitly, then remove only that demo partition.
ALTER TABLE partition_lab.orders_by_day ADD PARTITION (order_date='2026-09-22');
SHOW PARTITIONS partition_lab.orders_by_day;
SELECT COUNT(*) AS empty_partition_rows FROM partition_lab.orders_by_day WHERE order_date='2026-09-22';
ALTER TABLE partition_lab.orders_by_day DROP PARTITION (order_date='2026-09-22');
SHOW PARTITIONS partition_lab.orders_by_day;
