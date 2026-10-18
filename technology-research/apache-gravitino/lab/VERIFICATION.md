# Kết quả kiểm chứng lab

Kiểm chứng ngày **28/09/2026** trên Windows, Docker Desktop 4.47.0, Linux engine 28.4.0 và Docker Compose 2.39.4. Kết quả dưới đây là chạy thật trên stack `gravitino-learning`, không chỉ đối chiếu tài liệu.

## Kết quả

| Hạng mục | Kết quả quan sát |
|---|---|
| Cấu hình Compose | `docker compose config --quiet` thành công |
| Script và fixtures | PowerShell/Python parse thành công; các JSON payload hợp lệ |
| Dependency init | JDBC SHA-256 hợp lệ, init kết thúc exit 0 |
| Gravitino và PostgreSQL | Cả hai `healthy` |
| Bootstrap lặp lại | Object có sẵn được giữ, không conflict hoặc tạo thêm nguồn trùng |
| Discovery | Gravitino liệt kê `sales.orders` và `sales.customers` được tạo trước tại PostgreSQL |
| REST DDL → native SQL | REST tạo bảng; PostgreSQL INSERT và SELECT được 2 dòng |
| Native DDL → REST | Cột `native_column` thêm bằng SQL xuất hiện trong GET table |
| Tag | Tạo tag, gắn lên bảng nguồn và đọc lại tên tag thành công |
| Managed fileset | DELETE xóa thư mục và marker của fileset thử nghiệm |
| External fileset | DELETE giữ marker/file; đăng ký lại thành công |
| REST DROP table | Bảng thử nghiệm biến mất khỏi `information_schema.tables` |
| PostgreSQL dừng | Readiness `up`; list catalogs và GET fileset thành công; list PostgreSQL tables trả HTTP 500 |
| Gravitino dừng | PostgreSQL vẫn trả count `sales.orders = 3` qua SQL trực tiếp |
| Tạo lại container | `down` → `up` không xóa volume: tag marker, fileset registration, bytes JSONL và bảng nguồn vẫn còn trước khi bootstrap |
| Web UI endpoint | HTTP GET `/` trả 200; chưa kiểm thử tự động các thao tác click trong UI |
| Payload trong giáo trình | Đã chạy tạo schema/table, INSERT native, tạo/gắn tag, managed và external lifecycle qua `api.ps1` |

Log smoke test sau khi tạo lại container: [verification.log](verification.log). Tên bảng thử trong lần đó: `sales.smoke_3e8e3f922c9c`; script đã dọn bảng, tag và fileset thử. Các object tạm do thử payload (`workshop.notes`, `sensitive`, `scratch`) cũng được dọn để người học chạy bài từ đầu.

Trạng thái bàn giao: metalake `learning`, catalogs `pg_shop`/`lake_files`, bảng mẫu `orders` (3 dòng), `customers` (3 dòng), fileset external `incoming_events` và 2 dòng JSONL. PostgreSQL không publish cổng ra host; Gravitino bind loopback `19090`.

## Các chi tiết đã điều chỉnh theo runtime

- H2 storage path là tiền tố tên file: dùng `/entity-store/gravitino` để file nằm trong volume.
- Health response thực tế là `status: "up"`; parser xử lý không phân biệt hoa/thường.
- Fileset response thực tế dùng `managed`/`external`; request nhận `MANAGED`/`EXTERNAL`.
- JDBC pool minimum phải là số dương; lab dùng `1`.

Image Gravitino đã tải có digest:

```text
apache/gravitino:1.3.0
sha256:4ff340f1160600ecac8126c2a0c4b88ea2178d3f1954966af559bab526485af6
```

SHA-256 JAR đã tải từ Maven Central và ghim trong script init:

```text
postgresql-42.7.13.jar
6e0e4cc2d8cae902084f8a2b18728b073a6fd9d1f87c9d8bff8f298c18185b93
```

## Chưa được kiểm chứng bởi lab này

RBAC/identity provider, credential vending, Spark/Trino integration, Iceberg REST commit, cloud storage, HA/đa vùng, benchmark và backup/restore sau hỏng volume. H2 single-node không đại diện cấu hình production. Kết quả với PostgreSQL/fileset không tự bảo đảm cùng behavior ở mọi catalog provider.

Workspace chứa lab không phải Git repository tại thời điểm thực hiện; các file được tạo/sửa local, không commit hoặc push.
