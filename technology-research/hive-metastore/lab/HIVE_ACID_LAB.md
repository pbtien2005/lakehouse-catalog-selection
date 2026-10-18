# Thực hành Hive ACID

Lab dùng HiveServer2 làm client ACID, HMS + PostgreSQL giữ transaction state,
và volume `acid-warehouse` giữ file ORC. Bảng được tách khỏi lab non-ACID.

## 1. Mở Beeline

```powershell
docker compose exec hiveserver2-acid beeline -u "jdbc:hive2://localhost:10000/default"
```

## 2. Tạo database và bảng full ACID

Chạy từng câu trong Beeline:

```sql
CREATE DATABASE IF NOT EXISTS acid_lab
LOCATION 'file:///warehouse-acid/acid_lab.db';

CREATE TABLE acid_lab.orders (
  order_id BIGINT,
  customer STRING,
  amount DECIMAL(10,2)
)
CLUSTERED BY (order_id) INTO 2 BUCKETS
STORED AS ORC
TBLPROPERTIES ('transactional'='true');
```

Kiểm tra:

```sql
DESCRIBE FORMATTED acid_lab.orders;
```

Kết quả cần có `transactional=true`, loại managed table và định dạng ORC.

## 3. INSERT, UPDATE và DELETE

```sql
INSERT INTO acid_lab.orders VALUES
  (1, 'An', 100.00),
  (2, 'Binh', 250.00),
  (3, 'Chi', 80.00);

UPDATE acid_lab.orders SET amount = 120.00 WHERE order_id = 1;
DELETE FROM acid_lab.orders WHERE order_id = 2;

SELECT * FROM acid_lab.orders ORDER BY order_id;
```

Kết quả cuối cần còn order 1 với amount 120 và order 3 với amount 80.

## 4. Quan sát transaction state

Trong Beeline:

```sql
SHOW TRANSACTIONS;
SHOW LOCKS acid_lab.orders EXTENDED;
```

Trong PowerShell khác:

```powershell
docker compose exec postgres psql -U hive -d metastore
```

Trong psql:

```sql
SELECT * FROM "TXNS" ORDER BY "TXN_ID";
SELECT * FROM "TXN_TO_WRITE_ID" ORDER BY "T2W_TXNID";
SELECT * FROM "COMPLETED_TXN_COMPONENTS" ORDER BY "CTC_TXNID";
```

## 5. Quan sát base/delta files

Từ PowerShell:

```powershell
docker compose exec hiveserver2-acid ls -R /warehouse-acid/acid_lab.db/orders
```

Bạn cần thấy các thư mục/file thuộc `delta_*` và `delete_delta_*` sau CRUD.

## 6. Thử compaction

Trong Beeline:

```sql
ALTER TABLE acid_lab.orders COMPACT 'major' AND WAIT;
SHOW COMPACTIONS;
SELECT * FROM acid_lab.orders ORDER BY order_id;
```

Sau đó chạy lại lệnh `find`. Nếu compaction hoàn tất, sẽ xuất hiện `base_*` mới.

## Phạm vi

Lab dùng local filesystem volume để tập trung vào transaction, write ID và compaction.
Nó chưa chứng minh Hive ACID hoạt động tốt trên MinIO/S3 hoặc nhiều node.
