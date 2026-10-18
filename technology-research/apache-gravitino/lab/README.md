# Lab Apache Gravitino: học bằng quan sát hệ thống thật

Lab tiếng Việt, khoảng **2–3 giờ**, dành cho người đã biết SQL và Docker cơ bản. Bạn sẽ đăng ký một PostgreSQL đã có dữ liệu, tạo bảng qua Gravitino, quản lý fileset, gắn tag và kiểm tra điều gì xảy ra khi một thành phần dừng hoạt động.

## Bắt đầu trong PowerShell

Yêu cầu: Docker Desktop chạy **Linux containers**, Docker Compose v2, khoảng 3–4 GB RAM còn trống cho lab và Internet ở lần đầu. Không cần cài Java, Python, PostgreSQL hay Spark trên Windows. Image Gravitino chứa Python dùng cho REST client nhỏ của lab. Dung lượng image giải nén có thể lớn hơn nhiều dung lượng tải.

```powershell
cd 'D:\it\data engineer\apache polaris\technology-research\apache-gravitino\lab'
.\setup-env.ps1
docker compose up -d
docker compose exec -T gravitino python3 /lab/scripts/lab.py bootstrap
docker compose ps -a
.\verify.ps1
```

Nếu PowerShell chặn script, dùng `powershell -ExecutionPolicy Bypass -File .\setup-env.ps1` và tương tự với `verify.ps1`. Nếu container vừa khởi động chưa nhận `exec`, đợi vài giây rồi chạy lại bootstrap. Bootstrap đợi readiness, giữ nguyên object đã có và chỉ tạo object còn thiếu.

Mở **[Gravitino UI](http://localhost:19090)** → metalake `learning` → catalog `pg_shop` hoặc `lake_files`. API chạy cùng cổng. Container `init` ở trạng thái `Exited (0)` là bình thường; hai service còn lại phải `healthy`. UI có thể yêu cầu chọn metalake hoặc tải lại trang sau bootstrap.

**Bắt đầu học tại [01-bai-thuc-hanh.md](01-bai-thuc-hanh.md).** Đọc thêm [02-kien-truc-va-dap-an.md](02-kien-truc-va-dap-an.md) sau khi tự dự đoán kết quả. [VERIFICATION.md](VERIFICATION.md) ghi phạm vi kiểm chứng thực tế.

## Bạn sẽ học được gì?

| Bài | Thực hành | Điểm cần hiểu |
|---|---|---|
| 1 | Khám phá UI và REST | Metalake → catalog → schema → object |
| 2 | Đọc bảng PostgreSQL có sẵn | Federation, dữ liệu và metadata nguồn |
| 3 | Tạo schema/table qua REST | Provider ánh xạ API thành DDL ở nguồn |
| 4 | ALTER trực tiếp tại PostgreSQL | Metadata có thể thay đổi ngoài Gravitino |
| 5 | Managed và external fileset | Danh tính logic, đường dẫn vật lý, vòng đời file |
| 6 | Gắn tag lên bảng | Metadata quản trị và giới hạn của tag |
| 7 | Dừng PostgreSQL, dừng Gravitino | Control path, data path, phạm vi health check |
| 8 | Tạo lại container và xem volume | Persistence và phạm vi backup |

## Môi trường và phạm vi

| Thành phần | Phiên bản | Vai trò |
|---|---|---|
| Apache Gravitino | 1.3.0 | Unified REST API, UI, providers, entity store H2 |
| PostgreSQL | 16.4 | Nguồn dữ liệu `shop`, **không phải** entity store của Gravitino |
| PostgreSQL JDBC | 42.7.13 | Driver cho provider `jdbc-postgresql`, kiểm tra SHA-256 khi tải |
| alpine/curl | 8.21.0 | Init volume và tải JDBC driver một lần |

Gravitino chạy UID 1000, JVM tối đa 1 GB. Named volumes thuộc project Compose `gravitino-learning`; không dùng chung database/volume với các lab khác. Chỉ publish Gravitino trên `127.0.0.1:19090`; PostgreSQL dùng mạng nội bộ Compose. Đổi `GRAVITINO_PORT` trong `.env` nếu trùng cổng, rồi chạy lại `docker compose up -d`.

Lab đơn node dùng H2 để thấy rõ persistence. Chưa bật authentication/authorization; mật khẩu PostgreSQL được sinh ngẫu nhiên vào `.env`, không commit file này. Đây là môi trường local. Lab **không kiểm thử** HA, đa vùng, RBAC, credential vending, Spark/Trino connector hoặc Iceberg REST service. Những phần đó có giải thích và hướng mở rộng ở tài liệu kiến trúc. Cấu hình auxiliary service đang để trống.

## Kiểm tra tự động

```powershell
.\verify.ps1
```

Script bootstrap rồi tạo tên `smoke_<12 ký tự>` riêng cho mỗi lần chạy. Nó kiểm chứng: discovery bảng có sẵn; REST tạo bảng thật; SQL ghi/đọc 2 dòng; native ALTER được REST nhìn thấy; gắn tag; managed drop xóa thư mục; external drop giữ file; REST drop xóa bảng ở PostgreSQL. Thành công kết thúc bằng `PASS: all integration checks completed`.

Object thử nghiệm được dọn khi chạy thành công; bảng `orders/customers`, fileset `incoming_events` và bài làm của bạn được giữ. Nếu kiểm tra thất bại giữa chừng, tên object được in để bạn điều tra; script không xóa hàng loạt dữ liệu để che lỗi.

## Dừng, mở lại và reset

```powershell
docker compose stop
docker compose start
```

Hoặc `docker compose down` rồi `docker compose up -d`: dữ liệu trong named volumes vẫn còn. Giữ `.env` để mật khẩu khớp database đã khởi tạo.

**Chỉ khi muốn xóa toàn bộ dữ liệu của lab này và làm lại từ đầu:**

```powershell
docker compose down -v
docker compose up -d
docker compose exec -T gravitino python3 /lab/scripts/lab.py bootstrap
```

`down -v` xóa cả metadata, dữ liệu SQL, fileset và cache driver của project này. Chạy tại đúng thư mục lab; không cần dùng `docker system prune`.

## Khi gặp lỗi

| Triệu chứng | Kiểm tra và xử lý |
|---|---|
| Docker daemon không truy cập được | Mở Docker Desktop, chọn Linux containers, chạy `docker version` trong terminal của bạn |
| Pull bị `EOF` hoặc connection reset | Kiểm tra mạng/proxy rồi chạy lại `docker compose up -d`; không đổi tùy tiện tag |
| Init lỗi tải JAR/checksum | `docker compose logs init`; script chỉ đổi tên file tạm sau khi checksum đúng |
| Gravitino không healthy | `docker compose logs --tail 100 gravitino`; xem thêm lệnh đọc log dưới đây |
| `ClassNotFoundException: org.postgresql.Driver` | Driver cần nằm trong `catalogs/jdbc-postgresql/libs`; script startup đã liên kết đúng vị trí |
| HTTP 409 ở bài CREATE | Object đã tồn tại; dùng GET để tiếp tục hoặc chọn tên mới trong payload |
| HTTP 5xx lúc PostgreSQL đã dừng | Đây là lỗi dự kiến ở bài 7; chạy lại PostgreSQL, đợi healthy |
| Sai mật khẩu sau khi đổi `.env` | PostgreSQL chỉ dùng biến khởi tạo khi volume rỗng; khôi phục `.env` cũ hoặc reset lab có chủ đích |
| Không thấy file ở Windows | `/raw-files/...` là đường dẫn trong container/volume, không phải ổ D: |

```powershell
docker compose logs --tail 100 gravitino
docker compose exec -T gravitino sh -c 'tail -n 100 /opt/gravitino/logs/gravitino-server.log'
docker compose logs --tail 80 postgres init
```

## Tài liệu chính thức đã dùng

- [Overview 1.3.0](https://gravitino.apache.org/docs/1.3.0/overview/)
- [Docker image details](https://gravitino.apache.org/docs/1.3.0/docker-image-details/)
- [PostgreSQL catalog](https://gravitino.apache.org/docs/1.3.0/jdbc-postgresql-catalog/)
- [Relational API](https://gravitino.apache.org/docs/1.3.0/manage-relational-metadata-using-gravitino/)
- [Fileset API](https://gravitino.apache.org/docs/1.3.0/manage-fileset-metadata-using-gravitino/)
- [Tag API](https://gravitino.apache.org/docs/1.3.0/manage-tags-in-gravitino/)
- [Server configuration và health checks](https://gravitino.apache.org/docs/1.3.0/gravitino-server-config/)

Bản giải thích chuyên sâu đã có trong workspace: [apache-gravitino.md](../apache-gravitino.md).
