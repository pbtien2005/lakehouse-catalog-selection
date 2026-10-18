CREATE DATABASE IF NOT EXISTS storage_check LOCATION 's3a://warehouse/storage_check.db';
CREATE TABLE IF NOT EXISTS storage_check.customers (id BIGINT, name STRING) STORED AS PARQUET;
INSERT OVERWRITE TABLE storage_check.customers VALUES (1, 'An'), (2, 'Binh');
SELECT * FROM storage_check.customers ORDER BY id;
DESCRIBE FORMATTED storage_check.customers;
