# Rà soát bằng chứng cho hai recipe triển khai

Ngày đọc nguồn: **18/10/2026**. Phạm vi: bổ sung đường thực hiện có chứng cứ cho hai bài thực nghiệm. Đây là **đối chiếu tài liệu nguồn**, chưa chạy lại AWS, Docker, Spark hoặc notebook; chưa có chuyên gia độc lập duyệt độ đúng. Dữ liệu gốc và cả bảy scope được giữ lại.

## Các tệp và cách dùng

- [verified-path-evidence-2026-10-18.json](verified-path-evidence-2026-10-18.json): 15 claim mới, ba claim cũ được đối chiếu lại và bảy nguồn chính thức.
- [implementation-profiles-v1.json](implementation-profiles-v1.json): hai recipe nguyên vẹn. Mỗi binding phải có một claim cùng property chứng minh toàn bộ tổ hợp qualifier. Không lấy ưu điểm từ các đường không tương thích để ghép thành một lời giải.

Context của recipe dùng ID chuẩn: `aws_s3`, `local_filesystem`, `aws`, `local_lab`. Lớp intake phải ánh xạ tường minh input `s3`/`local_fs`; chọn một recipe không tự chứng minh storage, môi trường hay thao tác người dùng chưa khai báo.

Claim vẫn có `status: draft` để giữ phân biệt giữa đọc đối chiếu nguồn và duyệt chuyên gia. Trường `verification` ghi rõ nguồn đã được đọc lại, chưa kiểm thử runtime và chưa được con người phê duyệt. Không thêm score, weight hoặc tham số mô hình vào tri thức.

## Recipe AWS: Glue + EMR Serverless + Lake Formation

Nguồn [bài worked example AWS](https://aws.amazon.com/blogs/big-data/fine-grained-access-control-in-amazon-emr-serverless-with-aws-lake-formation/) dùng EMR 7.2.0, producer Glue catalog và consumer roles. Nguồn [tài liệu EMR](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/emr-serverless-lf-enable.html) xác định cơ chế FGAC và credential. [Lake Formation data filtering](https://docs.aws.amazon.com/lake-formation/latest/dg/data-filtering.html) giới hạn kết quả SELECT theo hàng/cột.

| Vai trò | Binding đã thu | Điều kiện cần giữ |
|---|---|---|
| Metadata Iceberg | `aws_glue_api`, load/create | Đúng catalog và IAM metadata |
| Spark đọc/ghi | `emr_iceberg_spark_session_catalog`, release `emr-7.2.0` | Runtime và IAM/S3 theo từng vai trò |
| Phân quyền đọc | `emr_serverless_lakeformation_fgac`, `filter_select_results` | Location đã đăng ký, bật integration và có grants/filters |
| Credential tạm | `lake_formation_get_data_access`, client `emr_serverless_spark` | Đường tích hợp LF, không phải credential tạm bất kỳ |

Các API theo vai trò có thể khác nhau trong cùng một bundle. Đặc biệt, không dùng claim full-table `GetTemporaryDataLocationCredentials` làm chứng cứ bộ lọc hàng/cột. Người đọc hạn chế quyền và người ghi ingestion là các vai trò khác nhau; bộ lọc SELECT không chứng minh mọi thao tác ghi an toàn.

EMR hiện tại có thay đổi credential cho nhiều DML tại mốc 7.12. Recipe giữ phạm vi bản 7.2.0 trong bài gốc, không áp hành vi bản mới ngược về bản cũ. Điều kiện phiên bản là dữ kiện nguồn, không phải giá trị mặc định để tối ưu kết quả.

## Recipe Nessie: native Spark + nhánh catalog trong local lab

[Spark via Iceberg](https://projectnessie.org/iceberg/spark/) có đường NessieCatalog, tạo bảng, INSERT/append và SELECT. [SQL extensions](https://projectnessie.org/guides/sql/) và [Transactions](https://projectnessie.org/guides/transactions/) chứng minh tạo/chuyển nhánh và công bố bằng merge. [Recipe server local](https://projectnessie.org/guides/try-nessie/) là chứng cứ chạy server cục bộ, không phải chứng nhận production.

Đường native dùng `nessie_api`; không lấy claim Spark chỉ connect qua REST để thay cho read qua native. Claim load và branching cũ được tái sử dụng, có metadata rà soát riêng, tránh tạo claim full trùng khóa. Native Spark dùng warehouse path; quyền và sự hiện diện của filesystem vẫn là điều kiện triển khai, chưa được dự án xác nhận.

Tài liệu có nhiều ví dụ version và grammar đổi từ 0.95.0. Profile ghi rõ phải chọn bộ Spark/Scala/Iceberg/extension tương thích. Bài legacy Dremio không được biến thành chứng cứ đã chạy binary Nessie hiện tại. Không diễn giải catalog branching thành SQL transaction đa bảng hoặc sao chép vật lý mọi data file.

## Cận dưới số bảng: dùng có giới hạn

Hai record `limits.quota` mới mang `observation_context.limit_kind: demonstrated_minimum`, **không phải quota tối đa**. AWS worked example nêu bảy ID bảng riêng trong cùng producer database/catalog; ví dụ native Nessie tạo và đọc ít nhất một bảng logic. Đây là cận dưới từ ví dụ nguồn công bố, chưa phải số đo độc lập.

- Nhu cầu chính xác không vượt cận dưới mới được chứng minh trong phạm vi recipe đó.
- Nhu cầu lớn hơn cận dưới phải giữ unknown, không suy none và không nội suy hiệu năng.
- Bucket `<100` còn bao gồm 99; ví dụ một hoặc bảy bảng không chứng minh toàn bộ bucket.
- Record Nessie mới ghi `supersedes_claim_ids` để thay đúng placeholder quota `null` cũ khi merge. Không xóa claim nguồn gốc hoặc biến cận dưới thành sức chứa vô hạn.

Quota tài khoản thực, headroom, region, retention và điều kiện production vẫn cần kiểm tra trước triển khai. Số bảng nguồn, release label, chiều dài và hash nguồn là metadata có provenance; các tham số chấm điểm tiếp tục lấy config hiện hữu.

## Truy vết và giới hạn

Mỗi claim có source URL, section/locator, ngày đọc và source ID. Registry nguồn giữ SHA-256 của phần văn bản chính sau chuẩn hóa whitespace, giúp nhận ra thay đổi trang. Chỉ lưu diễn giải ngắn và digest, không sao chép toàn văn tài liệu.

Không thêm claim `none` cho sáu catalog còn lại chỉ vì chưa tìm thấy feature. Không suy catalog chạy local chỉ từ engine local, hoặc suy không thể dùng AWS API từ on-prem. Profile không khớp chỉ loại recipe đó khỏi việc áp dụng, chưa chứng minh mọi cách triển khai của catalog đều thất bại. Hai recipe là danh mục mở, không phải danh sách đầy đủ mọi phương án.
