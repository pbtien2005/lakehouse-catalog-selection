# Lab Project Nessie + Iceberg

Môi trường thực hành local trên Docker Desktop (Linux containers):

| Thành phần | Phiên bản | Vai trò |
|---|---|---|
| Nessie | 0.108.8 | Iceberg REST Catalog, branch/tag/commit/merge |
| PostgreSQL | 16.4 | Lưu trạng thái catalog bằng JDBC2 |
| MinIO | RELEASE.2025-09-07T16-13-09Z | Lưu file dữ liệu và metadata Iceberg |
| Spark | 3.5.7, Scala 2.12, Java 17 | Spark SQL và PySpark |
| Iceberg | 1.11.0 | Định dạng bảng và client REST |
| Nessie Spark extensions | 0.108.8 | Lệnh quản lý reference trong Spark SQL |

Spark chạy `local[2]`, driver 1 GB. Nên dành ít nhất 4 GB RAM cho riêng lab, thêm RAM nếu chạy đồng thời các lab khác. Lần đầu cần Internet để tải image và ba JAR Maven; các lần sau dùng lại volume. Không cần cài Java/Spark/Python trên Windows.

## Khởi động trong PowerShell

```powershell
cd 'D:\it\data engineer\apache polaris\technology-research\project-nessie\lab'
.\setup-env.ps1
docker compose up -d
docker compose ps -a
```

`setup-env.ps1` tạo mật khẩu ngẫu nhiên trong `.env`, giữ nguyên nếu file đã tồn tại. Không đưa `.env` lên Git. Nếu PowerShell chặn script, chạy `powershell -ExecutionPolicy Bypass -File .\setup-env.ps1`.

`minio-init` và `jars-init` kết thúc với `Exited (0)` là bình thường. Đợi Spark hiển thị `healthy` rồi chạy bài kiểm tra.

## Truy cập

| Dịch vụ | Địa chỉ từ Windows |
|---|---|
| Nessie API config | http://localhost:19120/api/v2/config |
| Nessie references | http://localhost:19120/api/v2/trees |
| Iceberg REST, branch main | http://localhost:19120/iceberg/main/ |
| MinIO Console | http://localhost:19201 |
| MinIO S3 API | http://localhost:19200 |

Đăng nhập MinIO bằng `MINIO_ROOT_USER` và `MINIO_ROOT_PASSWORD` trong `.env`. Bucket `warehouse` được tạo tự động.

Các cổng chỉ bind vào `127.0.0.1`. Đây là lab local, Nessie chưa bật xác thực. PostgreSQL chỉ truy cập trong mạng Compose. Cấu hình S3 trả về cho Spark dùng hostname `minio`, vì vậy hãy chạy Spark trong container đã cấu hình.

Spark dùng warehouse mặc định do Nessie trả về. Không thêm `spark.sql.catalog.nessie.warehouse=warehouse`: với bộ phiên bản này, cấu hình đó gây lỗi prefix REST sau `USE REFERENCE`.

## Kiểm tra toàn bộ luồng

```powershell
docker compose exec -T spark /opt/spark/bin/spark-submit /opt/lab/scripts/smoke_test.py
```

Bài kiểm tra tạo namespace riêng mỗi lần, tạo bảng `orders`, ghi 2 dòng trên `main`, tạo branch và thêm dòng thứ 3. Sau đó xác nhận `main` vẫn có 2 dòng, merge branch và xác nhận `main` có 3 dòng, cuối cùng tạo tag. Thành công sẽ in `PASS:`. Dữ liệu kiểm tra được giữ lại để bạn xem; mỗi lần chạy tạo thêm một namespace/branch/tag.

Đã chạy thành công ngày 22/09/2026, bảng mẫu hiện có: `nessie.smoke_322a9749cc.orders` (3 dòng). Log lần kiểm tra nằm trong `smoke-test.log`. Cảnh báo deprecated signer properties đến từ cấu hình Nessie trả về; không làm thất bại thao tác đọc/ghi đã kiểm chứng.

## Thực hành SQL tương tác

```powershell
docker compose exec spark /opt/spark/bin/spark-sql
```

Chạy lần lượt trong Spark SQL, dùng tên mới nếu đã tạo trước đó:

```sql
CREATE NAMESPACE IF NOT EXISTS nessie.demo;
CREATE TABLE nessie.demo.orders (id BIGINT, amount DECIMAL(12,2)) USING iceberg;
INSERT INTO nessie.demo.orders VALUES (1, 100.00), (2, 250.00);
CREATE BRANCH dev IN nessie FROM main;
USE REFERENCE dev IN nessie;
INSERT INTO nessie.demo.orders VALUES (3, 75.00);
SELECT * FROM nessie.demo.orders;
USE REFERENCE main IN nessie;
SELECT * FROM nessie.demo.orders;
MERGE BRANCH dev INTO main IN nessie;
SELECT * FROM nessie.demo.orders;
CREATE TAG release_01 IN nessie FROM main;
LIST REFERENCES IN nessie;
SHOW LOG main IN nessie;
```

Gõ `quit;` để thoát. Mở PySpark bằng `docker compose exec spark /opt/spark/bin/pyspark`.

## Dừng và khởi động lại

```powershell
docker compose stop
docker compose start
```

Hoặc `docker compose down` rồi `docker compose up -d`; named volume giữ catalog PostgreSQL, dữ liệu MinIO và JAR. Không thêm `-v` vào lệnh `down` nếu muốn giữ dữ liệu. Giữ lại `.env` để mật khẩu tiếp tục khớp với PostgreSQL đã khởi tạo.

## Xem lỗi

```powershell
docker compose logs --tail 100 nessie
docker compose logs --tail 50 jars-init minio-init
docker compose ps -a
```

Nếu tải Maven/registry bị lỗi mạng, kiểm tra kết nối rồi chạy lại `docker compose up -d`. Thư viện tải hoàn tất được lưu trong volume, file tạm chỉ được đổi tên khi tải thành công.

## Tài liệu chính thức

- [Nessie với Iceberg REST](https://projectnessie.org/guides/try-nessie/)
- [Cấu hình server và JDBC2](https://projectnessie.org/nessie-latest/configuration/)
- [Nessie Spark SQL extensions](https://projectnessie.org/guides/sql/)
