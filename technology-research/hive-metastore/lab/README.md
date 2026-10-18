# Lab Hive Metastore + PostgreSQL + Spark + MinIO

## Khởi động từ PowerShell trong thư mục này

```powershell
.\setup-env.ps1
docker compose up -d
docker compose exec spark /opt/spark/bin/spark-sql
```

Compose tự tạo network, schema PostgreSQL và bucket warehouse.
Lần đầu cần Internet để tải image, PostgreSQL JDBC và thư viện S3A của Spark.
Spark chạy local[2] khi mở CLI; container chờ sẵn, không chạy cluster master/worker.

## Nơi lưu dữ liệu

- Metadata HMS: PostgreSQL, volume hms-full-lab_postgres-data.
- Dữ liệu bảng: MinIO bucket warehouse, volume hms-full-lab_minio-data.
- Cấu hình: conf/full.
- Mật khẩu: .env (được gitignore, không commit).

MinIO Console: http://localhost:19001. Thông tin đăng nhập trong .env.
MinIO API từ host: http://localhost:19000; từ container: http://minio:9000.
HMS từ host: thrift://localhost:19083; từ Spark: thrift://hive-metastore:9083.
Các cổng chỉ bind localhost. Đây là lab một người dùng; Spark/HMS dùng
credential quản trị MinIO để giảm số bước setup.

## Kiểm chứng

```powershell
docker compose exec spark /opt/spark/bin/spark-sql -f /opt/lab/scripts/check.sql
docker compose exec spark /opt/spark/bin/spark-sql -f /opt/lab/scripts/storage-check.sql
```

Bài storage-check tạo database riêng storage_check, ghi đè bảng mẫu customers
bằng 2 dòng rồi đọc lại. Chỉ chạy với dữ liệu lab.
Spark dùng Hive client 4.1.0 lấy từ image HMS qua volume hive-client.
Client mặc định của Spark có thể xem database nhưng không tương thích API get_table
của HMS này. HMS dùng Hadoop 3.4.1; Spark nạp S3A 3.4.2 khớp Hadoop Spark.
Thư viện tải về được cache trong volume spark-ivy để giữ lại khi tạo lại container.
File cấu hình HMS được mount trực tiếp vì entrypoint image thiếu lệnh find.

## Bài thử partition (đã chạy)

Script `scripts/partition-demo.sql` đã tạo bảng external `partition_lab.orders_by_day`:
- Ngày 2026-09-20: 2 dòng, tổng amount 350.00.
- Ngày 2026-09-21: 2 dòng, tổng amount 200.00.
- Thêm partition rỗng ngày 2026-09-22, xác nhận 0 dòng, rồi xóa đăng ký partition đó.
- EXPLAIN với bộ lọc ngày 2026-09-20 chỉ chọn location của ngày đó.

Đã đối chiếu PostgreSQL có đúng 2 partition và MinIO có file Parquet ở cả 2 prefix.
Marker rỗng của ngày 2026-09-22 còn trên MinIO sau khi DROP partition;
không nhầm xóa đăng ký metadata với xóa mọi object trên storage.
Không chạy lại toàn bộ script trên bảng đang tồn tại: CREATE sẽ dừng để tránh ghi lặp.

Xem kết quả trong Spark SQL:

```sql
SHOW PARTITIONS partition_lab.orders_by_day;
SELECT * FROM partition_lab.orders_by_day ORDER BY order_date, order_id;
```

Đối chiếu PostgreSQL từ PowerShell:

```powershell
Get-Content scripts/partition-metadata.sql | docker compose exec -T postgres psql -U hive -d metastore -v ON_ERROR_STOP=1
```

## Môi trường cũ

Stack mới dùng project hms-full-lab, network/volume và cổng riêng.
Không tự chuyển metadata từ Derby của container hive-metastore cũ.
Các container cũ vẫn nguyên trạng; lab mới ban đầu là catalog trống.
Cấu hình Spark-only trước đây giữ ở compose.spark-only.yaml và conf/spark-defaults.conf.
Vào stack mới bằng docker compose exec spark, không dùng tên container Spark cũ.

## Dừng và chạy lại

```powershell
docker compose stop
docker compose start
```

docker compose down gỡ container/network nhưng giữ named volumes.
Không thêm -v nếu muốn giữ metadata và dữ liệu.
