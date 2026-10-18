# Thực hành: từ catalog đến nguồn dữ liệu

Chạy các lệnh dưới đây trong PowerShell, tại thư mục `lab`, sau phần khởi động trong README. Mỗi bài gồm dự đoán → thao tác → quan sát → giải thích. Hãy ghi dự đoán trước khi xem [đáp án](02-kien-truc-va-dap-an.md).

`api.ps1` là wrapper rất mỏng: gọi Python trong container, gửi HTTP đến `127.0.0.1:8090`, kiểm tra HTTP/code và in JSON. Nó không giả lập Gravitino. Các payload nằm trong `payloads/` để bạn xem và sửa, tránh lỗi escape JSON trong PowerShell.

## Bài 1 — Mô hình đối tượng và đường đi của request · 15 phút

Mở [UI](http://localhost:19090), chọn metalake `learning`. Tìm `pg_shop` và `lake_files`; quan sát `type`, `provider`, schema và object con.

```powershell
.\api.ps1 GET /api/metalakes
.\api.ps1 GET /api/metalakes/learning/catalogs
.\api.ps1 GET /api/metalakes/learning/catalogs/pg_shop
.\api.ps1 GET /api/metalakes/learning/catalogs/pg_shop/schemas
.\api.ps1 GET /api/metalakes/learning/catalogs/lake_files/schemas/landing/filesets
```

Kết quả mong đợi: một metalake `learning`; catalog relational dùng `jdbc-postgresql`; catalog fileset dùng `fileset`; PostgreSQL có schema `sales`; fileset có `incoming_events`. Schema hệ thống PostgreSQL có thể xuất hiện tùy bộ lọc provider.

Gọi API trực tiếp từ Windows để thấy wrapper không phải yêu cầu bắt buộc:

```powershell
$headers = @{ Accept = 'application/vnd.gravitino.v1+json' }
Invoke-RestMethod -Uri 'http://localhost:19090/api/metalakes' -Headers $headers | ConvertTo-Json -Depth 10
```

**Tự trả lời:** `pg_shop` có phải tên database PostgreSQL không? `RELATIONAL` khác `jdbc-postgresql` thế nào? Nếu thay PostgreSQL bằng Hive, lớp nào đổi?

## Bài 2 — Đăng ký nguồn có sẵn không sao chép dữ liệu · 15 phút

`sql/01-seed.sql` tạo các bảng trong PostgreSQL trước khi bootstrap đăng ký catalog. Dự đoán Gravitino có nhìn thấy chúng mà không cần tạo lại từng bảng hay không.

```powershell
.\api.ps1 GET /api/metalakes/learning/catalogs/pg_shop/schemas/sales/tables
.\api.ps1 GET /api/metalakes/learning/catalogs/pg_shop/schemas/sales/tables/orders
docker compose exec -T postgres psql -X -U lab -d shop -c 'SELECT * FROM sales.orders ORDER BY id;'
docker compose exec -T postgres psql -X -v ON_ERROR_STOP=1 -U lab -d shop -f /lab/sql/02-query.sql
```

Quan sát:

- REST `GET .../orders` trả tên, kiểu cột, comment, properties và audit; không trả ba dòng đơn hàng.
- PostgreSQL trả ba đơn; tổng đơn đã thanh toán: An `120000.00`, Binh `250000.00`.
- Phép JOIN/aggregate do PostgreSQL thực thi. Lệnh `psql` đi thẳng đến PostgreSQL, không đi qua unified REST API.

**Tự trả lời:** thêm bảng vào Gravitino có khiến dữ liệu được chuyển sang H2 không? Tại sao một metadata API không có endpoint `SELECT * FROM orders`?

## Bài 3 — Unified API tạo DDL thật tại nguồn · 20 phút

Mở hai payload trước khi chạy:

```powershell
Get-Content .\payloads\create-schema.json
Get-Content .\payloads\create-table.json
.\api.ps1 POST /api/metalakes/learning/catalogs/pg_shop/schemas payloads/create-schema.json
.\api.ps1 POST /api/metalakes/learning/catalogs/pg_shop/schemas/workshop/tables payloads/create-table.json
docker compose exec -T postgres psql -X -U lab -d shop -c '\d workshop.notes'
docker compose exec -T postgres psql -X -v ON_ERROR_STOP=1 -U lab -d shop -c "INSERT INTO workshop.notes VALUES (1,'DDL through Gravitino, DML through PostgreSQL');"
docker compose exec -T postgres psql -X -U lab -d shop -c 'SELECT * FROM workshop.notes;'
```

Kết quả: schema và bảng thật tồn tại trong PostgreSQL; `long` ánh xạ thành `bigint`, `string` thành `text`. REST thực hiện DDL qua provider, còn INSERT thực hiện tại nguồn bằng SQL. Nếu chạy bài lần hai, CREATE trả 409 vì trùng tên: GET object để tiếp tục; không cần reset cả lab.

Thử quan sát comment tại nguồn:

```powershell
docker compose exec -T postgres psql -X -U lab -d shop -c "SELECT obj_description('workshop.notes'::regclass);"
```

Bạn có thể thấy dấu định danh nội bộ Gravitino trong comment. Giữ nguyên phần đó; provider dùng nó để liên kết metadata. [Chi tiết PostgreSQL provider](https://gravitino.apache.org/docs/1.3.0/jdbc-postgresql-catalog/).

**Tự trả lời:** `DROP TABLE` qua Gravitino có chỉ xóa một dòng đăng ký hay có thể xóa bảng thật? Provider có bảo đảm mọi kiểu dữ liệu chung đều hợp lệ trên PostgreSQL không?

## Bài 4 — Thay đổi xuất phát từ hệ thống nguồn · 15 phút

```powershell
docker compose exec -T postgres psql -X -v ON_ERROR_STOP=1 -U lab -d shop -f /lab/sql/03-source-change.sql
.\api.ps1 GET /api/metalakes/learning/catalogs/pg_shop/schemas/sales/tables/orders
```

Kết quả mong đợi: REST trả thêm cột `source_note`. Kiểm tra dữ liệu:

```powershell
docker compose exec -T postgres psql -X -U lab -d shop -c 'SELECT id,source_note FROM sales.orders ORDER BY id;'
```

Dòng 1 có `changed at source`; những dòng khác NULL. Lab tắt entity cache để việc quan sát dễ hơn; kết quả này không chứng minh mọi provider/cache đều đồng bộ tức thì.

**Tự trả lời:** nếu ứng dụng vẫn dùng SQL trực tiếp, ai kiểm soát quyền ở đường truy cập đó? Backup H2 có khôi phục được cột và dữ liệu vừa sửa không?

## Bài 5 — Fileset: tên logic, đường dẫn và vòng đời · 25 phút

```powershell
.\api.ps1 GET /api/metalakes/learning/catalogs/lake_files/schemas/landing/filesets/incoming_events
docker compose exec -T gravitino cat /raw-files/external/incoming/events.jsonl
```

REST trả location; `cat` đọc bytes từ volume. `file:/...` và `file:///...` có thể được thư viện chuẩn hóa, không nên so sánh URI bằng chuỗi đơn giản. Fileset này chứa JSONL, chưa tự trở thành bảng Iceberg hay bảng SQL.

### 5A. Xóa đăng ký external

Dự đoán file có còn sau lệnh DELETE:

```powershell
.\api.ps1 DELETE /api/metalakes/learning/catalogs/lake_files/schemas/landing/filesets/incoming_events
docker compose exec -T gravitino cat /raw-files/external/incoming/events.jsonl
.\api.ps1 POST /api/metalakes/learning/catalogs/lake_files/schemas/landing/filesets payloads/create-external-fileset.json
```

Kết quả: file vẫn tồn tại; lệnh POST cuối đăng ký lại external fileset. Chỉ áp dụng kết luận này cho thao tác/fileset đã thử, không suy rộng sang xóa schema, catalog hay tài nguyên khác.

### 5B. Xóa managed fileset

Chỉ dùng thư mục scratch của bài này vì DELETE sẽ xóa file vật lý:

```powershell
.\api.ps1 POST /api/metalakes/learning/catalogs/lake_files/schemas/landing/filesets payloads/create-managed-fileset.json
docker compose exec -T gravitino sh -c 'echo lab-marker > /raw-files/managed/scratch/marker.txt'
docker compose exec -T gravitino cat /raw-files/managed/scratch/marker.txt
.\api.ps1 DELETE /api/metalakes/learning/catalogs/lake_files/schemas/landing/filesets/scratch
docker compose exec -T gravitino sh -c 'if test -e /raw-files/managed/scratch; then echo STILL_EXISTS; else echo REMOVED; fi'
```

Kết quả: `REMOVED`. Không trỏ managed fileset vào thư mục có dữ liệu quý giá. Trong lab, đây là volume riêng và đường dẫn disposable.

**Tự trả lời:** metadata fileset nằm ở đâu? File ở đâu? Vì sao xóa managed và external có kết quả khác nhau?

## Bài 6 — Tag là metadata quản trị · 15 phút

```powershell
.\api.ps1 POST /api/metalakes/learning/tags payloads/create-tag.json
.\api.ps1 POST /api/metalakes/learning/objects/table/pg_shop.sales.orders/tags payloads/attach-tag.json
.\api.ps1 GET /api/metalakes/learning/objects/table/pg_shop.sales.orders/tags
docker compose exec -T postgres psql -X -U lab -d shop -c 'SELECT * FROM sales.orders ORDER BY id;'
```

Kết quả: object có tag `sensitive`, nhưng SELECT vẫn thấy dữ liệu. Nếu tag/association đã có, bỏ qua POST gây conflict và dùng GET. Tag dùng để phân loại; lab chưa cấu hình một policy engine hay data masking dựa trên tag. Tag ở đây cũng khác tag tham chiếu commit của Nessie.

**Tự trả lời:** authentication, authorization và classification khác nhau thế nào? Cần enforce ở đâu nếu người dùng vẫn truy cập trực tiếp PostgreSQL?

## Bài 7 — Thí nghiệm lỗi để nhận diện ranh giới · 20 phút

### 7A. Nguồn PostgreSQL dừng, Gravitino còn chạy

Ghi dự đoán cho từng lệnh GET. Dùng `finally` để luôn bật lại nguồn sau thí nghiệm:

```powershell
docker compose stop postgres
try {
    .\api.ps1 GET /api/health/ready
    .\api.ps1 GET /api/metalakes/learning/catalogs
    .\api.ps1 GET /api/metalakes/learning/catalogs/lake_files/schemas/landing/filesets/incoming_events
    .\api.ps1 GET /api/metalakes/learning/catalogs/pg_shop/schemas/sales/tables
} finally {
    docker compose start postgres
}
```

Lệnh list bảng PostgreSQL phải báo lỗi; PowerShell có thể in exception màu đỏ, đó là kết quả dự kiến. Readiness của server có thể vẫn `up`: nó kiểm tra entity store H2, không chứng nhận mọi nguồn JDBC đều hoạt động. Catalog registration và fileset vẫn đọc được. [Phạm vi health check](https://gravitino.apache.org/docs/1.3.0/gravitino-server-config/).

Sau khi PostgreSQL healthy, gọi lại list tables. Nếu pool giữ connection lỗi, đợi vài giây rồi thử lại. Trong trường hợp cần, `docker compose restart gravitino` tạo lại pool; thao tác này không sửa được một nguồn vẫn đang chết.

### 7B. Gravitino dừng, nguồn còn chạy

```powershell
docker compose stop gravitino
try {
    docker compose exec -T postgres psql -X -U lab -d shop -c 'SELECT count(*) FROM sales.orders;'
} finally {
    docker compose start gravitino
}
docker compose exec -T gravitino python3 /lab/scripts/lab.py wait
```

Kết quả: SQL vẫn trả `3` nếu bạn chưa tự sửa dữ liệu mẫu. UI/API không khả dụng khi Gravitino dừng. Client truy cập trực tiếp nguồn vẫn chạy được; **không suy ra** mọi Spark/Trino client tích hợp Gravitino đều hoạt động khi server chết, vì chúng có thể cần resolve catalog/credentials mới.

## Bài 8 — Persistence khi tạo lại container · 15 phút

Sau bài 6, ghi lại schema `workshop`, tag `sensitive`, số dòng `orders` và nội dung file JSONL. Sau đó:

```powershell
docker compose down
docker compose up -d
docker compose exec -T gravitino python3 /lab/scripts/lab.py wait
.\api.ps1 GET /api/metalakes/learning/catalogs
.\api.ps1 GET /api/metalakes/learning/objects/table/pg_shop.sales.orders/tags
docker compose exec -T postgres psql -X -U lab -d shop -c 'SELECT count(*) FROM sales.orders;'
docker compose exec -T gravitino cat /raw-files/external/incoming/events.jsonl
docker compose exec -T gravitino ls -lh /entity-store
```

Không chạy bootstrap trước các lệnh GET này: ta muốn chứng minh object được giữ lại, không phải được tạo lại. Kết quả mong đợi: catalog, tag, dữ liệu SQL và file đều còn nhờ các volume riêng. File H2 có tên dạng `gravitino.mv.db`.

**Tự trả lời:** chỉ sao lưu volume entity store có đủ khôi phục toàn bộ hệ thống không? H2 một node có chứng minh HA/geo-distribution chưa?

## Bài tổng kết — Vẽ lại kiến trúc không nhìn tài liệu

Vẽ các thành phần và mũi tên cho ba thao tác: GET table, CREATE table và SELECT rows. Ghi nơi lưu từng loại: catalog registration, SQL table definition, SQL rows, tag, fileset location và bytes JSONL.

Bạn hoàn thành khi giải thích được cả tám kết quả quan sát, chỉ đúng provider và hệ thống có thẩm quyền, đồng thời phân biệt unified API với Iceberg REST. Có thể chạy `verify.ps1` để kiểm tra lại hệ thống sau các bài.
