---
title: Cơ sở tri thức lớp 1 — bản dữ liệu từ tài liệu chính thức
date: 2026-10-17
revision: layer1-v3-data-2026-10-17-r1
status: documentation-based-draft
tags: [lakehouse, catalog, knowledge-base, layer-1]
---

# Cơ sở tri thức lớp 1 cho 7 công nghệ catalog

Đã biên soạn **203 claim cho 7 công nghệ**, dựa trên **61 URL nguồn chính thức** được đọc chọn lọc ngày **17/10/2026**: 173 claim có kết luận trong phạm vi xác định, 30 claim ghi rõ `unknown`/`null`. Mọi claim vẫn là `draft`; đây là kết quả đọc tài liệu, chưa phải kiểm chứng runtime hoặc duyệt độc lập.

Yêu cầu ghi “6 công nghệ” nhưng liệt kê **7 mục**. Bản dữ liệu giữ đủ danh sách và tách **Unity Catalog OSS** khỏi **Unity Catalog trên Databricks**. Phạm vi Databricks ở bản này là **AWS**.

## 1. Các artifact và cách đọc

| File | Vai trò |
|---|---|
| [layer-1-data.json](layer-1-data.json) | Dữ liệu có thẩm quyền: `manifest`, `scopes`, `claims`; evidence nhúng trong từng claim |
| [layer-1-properties.json](layer-1-properties.json) | Từ điển chung, giữ 11 nhóm và 37 thuộc tính |
| [layer-1-sources.md](layer-1-sources.md) | Danh mục nguồn với liên kết trực tiếp để người đọc kiểm tra |
| [layer-1-source-register.json](layer-1-source-register.json) | Inventory URL, tên trang, phạm vi tài liệu và ngày đọc; không thay evidence của claim |
| [layer-1-coverage.md](layer-1-coverage.md) | Bảng kiểm kê 37 thuộc tính × 7 scope, phân biệt đã thu/chưa thu |
| [layer-1-coverage.json](layer-1-coverage.json) | ID claim và khoảng trống của từng ô để đọc bằng máy |
| [layer-1-data-validation.json](layer-1-data-validation.json) | Kết quả kiểm tra cấu trúc và tham chiếu |
| [validate-layer-1-data.py](validate-layer-1-data.py) | Chạy lại kiểm tra và tái tạo các báo cáo inventory |

`full` chỉ có nghĩa hợp đồng **đúng với qualifier và điều kiện đã ghi** có căn cứ tài liệu. `none` cũng cần nguồn khẳng định giới hạn; không xuất hiện trong nguồn không phải `none`. Số claim và số URL không phải điểm phù hợp hoặc độ tin cậy xác suất.

## 2. Phạm vi bằng chứng đã chọn

| Công nghệ | Scope | Claim có kết luận | Claim unknown/null |
|---|---|---:|---:|
| Apache Polaris | OSS, self-managed, **1.7.0** | 29 | 4 |
| Apache Gravitino | OSS, self-managed, **1.1.0** | 30 | 5 |
| Project Nessie | OSS, self-managed, tài liệu theo ngày đọc | 24 | 5 |
| Unity Catalog OSS | OSS, self-managed, tài liệu theo ngày đọc | 22 | 5 |
| Unity Catalog trên Databricks | Managed, **AWS**, tài liệu theo ngày đọc | 28 | 4 |
| AWS Glue Data Catalog | Managed, tài liệu theo ngày đọc; Lake Formation là đường tích hợp có điều kiện | 22 | 3 |
| Apache Hive Metastore | OSS, self-managed, tài liệu theo ngày đọc và ghi chú phiên bản của từng trang | 18 | 4 |

Polaris 1.7.0 và Gravitino 1.1.0 là baseline bằng chứng được chọn, **không phải tuyên bố phiên bản mới nhất**. Scope `as_of` không chứng minh tính năng tồn tại trong mọi release. Các hướng dẫn HMS có nội dung lịch sử; phải kiểm tra lại phiên bản triển khai trước khi dùng làm điều kiện bắt buộc.

Từ điển được cập nhật nhỏ lên `v3.1`: thêm qualifier tùy chọn `table_type` và `metadata_representation` ở ba property liên quan format/engine/vending. Nhờ đó `format=iceberg` vẫn khác `table_type=managed/foreign`; `format=delta` với metadata UniForm không bị biến thành hỗ trợ Iceberg native. Các ID, kiểu giá trị, rubric và số lượng property giữ nguyên. Vắng qualifier tùy chọn **không** có nghĩa wildcard.

## 3. Những ranh giới quan trọng đã giữ trong dữ liệu

- **Polaris:** entry Delta qua Generic Tables và đường Spark client có điều kiện beta riêng; không dùng một entry metadata để suy mọi thao tác Delta. [Generic Table 1.7.0](https://polaris.apache.org/releases/1.7.0/generic-table/), [Polaris Spark Client 1.7.0](https://polaris.apache.org/releases/1.7.0/polaris-spark-client/)
- **Gravitino:** API quản trị Iceberg catalog và Iceberg REST là các đường khác nhau. Vending của connector Spark riêng không được gộp với Spark dùng Iceberg REST. [Iceberg catalog 1.1.0](https://gravitino.apache.org/docs/1.1.0/lakehouse-iceberg-catalog/), [Credential vending 1.1.0](https://gravitino.apache.org/docs/1.1.0/security/credential-vending/)
- **Nessie:** claim atomic nhiều bảng chỉ ghi cho việc công bố nhiều content updates trong một catalog commit. Transaction SQL của Spark được giữ unknown khi thiếu chứng minh end-to-end. [Transactions](https://projectnessie.org/guides/transactions/)
- **Unity Catalog OSS:** đường đọc Delta UniForm qua Iceberg REST có qualifier riêng; không dùng để kết luận ghi Iceberg native. [UniForm tables](https://docs.unitycatalog.io/usage/tables/uniform/)
- **Databricks:** managed Iceberg, foreign Iceberg và Delta bật Iceberg reads được tách khi ghi khả năng đọc/ghi. Phân quyền hàng/cột đã thu cho đường compute Databricks, chưa suy sang mọi external client. [Iceberg client access](https://docs.databricks.com/aws/en/external-access/iceberg), [Row filters and column masks](https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks)
- **Glue:** IAM, Lake Formation filtering và Lake Formation vending là các cơ chế/đường truy cập riêng. Claim vending cần location đã đăng ký và bảng Glue liên kết, không là tính năng mặc định của mọi Glue client. [IAM](https://docs.aws.amazon.com/glue/latest/dg/security-iam.html), [Data filtering](https://docs.aws.amazon.com/lake-formation/latest/dg/data-filtering.html), [GetTemporaryDataLocationCredentials](https://docs.aws.amazon.com/lake-formation/latest/APIReference/API_GetTemporaryDataLocationCredentials.html)
- **HMS:** metastore cho engine đọc Iceberg/Delta/Hudi không đồng nghĩa HMS thực thi mọi transaction hoặc quyền dữ liệu của các format. [Metastore Administration](https://hive.apache.org/docs/latest/admin/adminmanual-metastore-3-0-administration/), [Trino Iceberg](https://trino.io/docs/current/connector/iceberg.html), [Trino Delta Lake](https://trino.io/docs/current/connector/delta-lake.html), [Trino Hudi](https://trino.io/docs/current/connector/hudi.html)

## 4. Những chỗ không ép thành kết luận

### Gravitino 1.1.0: mô tả metadata authorization chưa thống nhất

Trang Access Control có một đoạn mô tả không kiểm tra quyền metadata khi nhận request, nhưng phần Built-in Authorization trên cùng trang mô tả cách bật kiểm tra quyền. Hai nội dung chưa đủ nhất quán để ghi một kết luận tổng quát cho unified REST. [Access Control 1.1.0](https://gravitino.apache.org/docs/1.1.0/security/access-control/)

Claim `cl_gravitino_oss_1_1_0_unified_authz_unresolved` giữ **unknown**. Các claim riêng cho auxiliary/standalone Iceberg REST dựa trên phần prerequisites và flow của tài liệu dịch vụ REST, không dùng claim này để suy qua lại. [Iceberg REST access control](https://gravitino.apache.org/docs/1.1.0/iceberg-rest-service/#access-control)

### Databricks: credential vending cho foreign Iceberg

Trang Iceberg client access ghi foreign Iceberg không hỗ trợ credential vending; bảng Supported access types của trang credential vending lại liệt kê read cho foreign Iceberg. Bản này chưa phân giải được sự khác nhau về endpoint hoặc điều kiện áp dụng. [Iceberg client access](https://docs.databricks.com/aws/en/external-access/iceberg), [Credential vending](https://docs.databricks.com/aws/en/external-access/credential-vending)

Claim `cl_unity_databricks_aws_2026_10_17_foreign_vend` giữ **unknown**, kèm cả hai nguồn. Không dùng mâu thuẫn này để phủ nhận vending cho mọi loại bảng.

### Unity Catalog OSS: hợp đồng vending chặt hơn tên tính năng

Trang server configuration mô tả trả credential theo bucket cấu hình; trang Spark có đường cloud/role. Chưa đủ bằng chứng cho phạm vi từng bảng và quyền caller ở mọi cấu hình. [Server configuration](https://docs.unitycatalog.io/server/configuration/), [Spark integration](https://docs.unitycatalog.io/integrations/unity-catalog-spark/)

Vì property `storage.credential_vending` yêu cầu đồng thời credential tạm thời và giới hạn phạm vi, claim `cl_unity_oss_2026_10_17_s3_vend_unknown` giữ **unknown**. Đây là giới hạn của bằng chứng thu thập, không phải kết luận OSS không có tính năng mang tên credential vending.

## 5. Khoảng trống có chủ đích

Bản này là nền dữ liệu ban đầu cho cả 7 công nghệ, chưa thu đủ mọi thuộc tính và mọi tổ hợp engine × format × thao tác × storage. [Bảng coverage](layer-1-coverage.md) hiển thị phần còn thiếu, thay vì điền mặc định.

- Chưa thu bộ đường streaming đủ qualifier; không gắn cờ streaming chung cho từng catalog.
- Chưa có bộ số đo hiệu năng hoặc giờ công tương đương; các quantity tương ứng là `null`.
- Chưa biên soạn đơn giá theo region/tier hoặc TCO; OSS không được gán chi phí bằng 0.
- Quota đã thu cho Glue/Databricks giữ đúng phạm vi và khả năng điều chỉnh; không thay quota bằng số bảng chạy demo.
- HA/DR, TLS, migration preserving grants/snapshot history, support/EOL và khả năng tổ hợp end-to-end cần nguồn bổ sung ở những ô chưa thu.
- Các URL lỗi hoặc không lấy được nội dung không được dùng để chứng minh claim. Không có bản chụp đầy đủ của upstream pages trong revision này; ngày đọc và locator giúp quay lại nguồn nhưng không đóng băng nội dung website.

## 6. Kiểm tra đã thực hiện

[Báo cáo kiểm tra](layer-1-data-validation.json) không phát hiện lỗi cấu trúc: JSON parse và không trùng key; scope/property hợp lệ; qualifier đúng từ điển; không trộn `level`/`value`; quantity đã biết có đơn vị/context; mọi claim có kết luận đều có evidence chính thức; nguồn khớp inventory; không trùng hoặc mâu thuẫn ở exact claim key; không nhúng score/weight vào facts.

Chạy lại từ thư mục bất kỳ:

```powershell
python "D:/it/data engineer/apache polaris/system-selection/research/catalog-knowledge-base/validate-layer-1-data.py" --write-reports
```

Kiểm tra này **không tự chứng minh nội dung nguồn kéo theo claim** và không gọi dịch vụ catalog. Các mâu thuẫn nội dung được giữ ở mục 4. Lớp 2/3 chưa được nối với bộ dữ liệu này; chưa sinh shortlist, ranking hoặc thay đổi input đã chốt.
