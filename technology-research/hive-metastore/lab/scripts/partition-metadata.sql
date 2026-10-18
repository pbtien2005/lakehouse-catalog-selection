SELECT d."NAME" AS database_name, t."TBL_NAME", k."PKEY_NAME", k."PKEY_TYPE"
FROM "DBS" d JOIN "TBLS" t ON t."DB_ID" = d."DB_ID"
JOIN "PARTITION_KEYS" k ON k."TBL_ID" = t."TBL_ID"
WHERE d."NAME" = 'partition_lab' AND t."TBL_NAME" = 'orders_by_day';

SELECT p."PART_NAME", v."PART_KEY_VAL", s."LOCATION"
FROM "PARTITIONS" p JOIN "TBLS" t ON t."TBL_ID" = p."TBL_ID"
JOIN "DBS" d ON d."DB_ID" = t."DB_ID"
JOIN "SDS" s ON s."SD_ID" = p."SD_ID"
JOIN "PARTITION_KEY_VALS" v ON v."PART_ID" = p."PART_ID"
WHERE d."NAME" = 'partition_lab' AND t."TBL_NAME" = 'orders_by_day'
ORDER BY p."PART_NAME", v."INTEGER_IDX";
