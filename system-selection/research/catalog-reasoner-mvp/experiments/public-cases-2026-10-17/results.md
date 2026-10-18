# Kết quả thực nghiệm hồ sơ dựa trên nguồn công khai

**Đã thực thi pipeline Python của dự án. Chưa có kết luận chọn catalog chắc chắn từ các hồ sơ này.** Không sửa KB, mapping, thuật toán, trọng số, config hoặc tập dữ liệu đã khóa. Hash trước/sau và config nguyên vẹn được ghi trong [run-manifest.json](results/run-manifest.json).

## Kết quả quan sát

| Hồ sơ | Yêu cầu sau Lớp 2 | Eligible | Conditional | Excluded | Chấm điểm SOFT |
|---|---|---|---|---|---|
| PUBLIC-LAB-01 | 7 HARD | 0 | 7 | 0 | Không có SOFT; score/top rate/regret = null |
| PUBLIC-LAB-02 | 5 HARD | 0 | 7 | 0 | Không có SOFT; score/top rate/regret = null |
| PUBLIC-LAB-02-SOFT | 4 HARD + 1 SOFT | 0 | 7 | 0 | Cả bảy cùng khoảng [0, 1] |

Từng lần chạy dùng seed và ngân sách kịch bản trong config gốc, được echo trong mỗi JSON. Đây là kết quả của bộ config cụ thể, không phải thông số đo được từ hai workload. Mỗi hồ sơ chạy lặp theo experiment-config và cho cùng toàn bộ JSON. `status: ok` chỉ xác nhận pipeline chấp nhận và xử lý input; không có nghĩa có ứng viên đủ điều kiện triển khai.

## Phát hiện từ bài 1

**Đạt về ánh xạ mục tiêu:** có hai yêu cầu quyền đọc riêng `R-I07-column-spark`, `R-I07-row-spark` và yêu cầu `R-I08-vending`. Không diễn giải chia sẻ nhiều tài khoản thành federation.

**Thông tin nguồn có nhưng form chưa chuyển được:** storage được giữ ở hồ sơ nguồn, nhưng payload hiện không có field này. Lớp 2 trả một unresolved `I08 / unknown_storage`; cloud AWS không tự được chuyển thành S3. Do đó credential vending chưa sẵn sàng để kết luận. Đây là mất thông tin khi chuyển từ mô tả bài toán sang giao diện, không phải người điền quên một câu đang có.

**Khớp nghĩa còn thiếu:** yêu cầu phân quyền dùng `action: read` trong khi miền giá trị tương ứng chưa được quy đổi đủ; trace có `coverage_gap`. Quota của một số ứng viên không cùng boundary catalog. API cho đọc Spark/load Iceberg vẫn mở nên các claim ở một path chưa bao phủ mọi trường hợp cho phép.

Glue và Unity Catalog Databricks có HARD môi trường AWS được xác lập; các yêu cầu khác vẫn có điều kiện. Glue trong bài gốc đi cùng Lake Formation và enforcement của EMR; không thể rút gọn toàn bộ lời giải thành mọi đường truy cập của Glue đều đạt.

Đối chiếu: [JSON đầy đủ](results/PUBLIC-LAB-01.json), [requirements](results/PUBLIC-LAB-01.requirements.json). Tìm `candidate_id: aws_glue_data_catalog`, `R-I07-column-spark`, `R-I07-row-spark`, `R-I08-vending` và `unresolved_inputs`.

## Phát hiện từ bài 2

**Đạt về ánh xạ ưu tiên:** `R-I10-branching` là HARD trong ca chính và SOFT trong biến thể. Hai payload chỉ khác rank; biến thể có weight thấp từ config, không đặt thêm weight riêng. Không phát sinh yêu cầu `multi_table_atomic` ngoài phạm vi.

**Nessie có claim hỗ trợ, nhưng chưa được chốt đường thực thi:** claim `cl_nessie_oss_2026_10_17_branch` ghi full cho `api: nessie_api`, `object_scope: catalog`. Trace của `R-I10-branching` nhận đúng claim này. Tuy nhiên `api` trong requirement là null, miền mở vẫn còn trường hợp chưa có claim; candidate binding hiện chỉ được ghi trace. Tổng hợp vì thế vẫn là unknown [none, full]. **Đây không phải bằng chứng Nessie thiếu branching. Bổ sung thêm một claim full cùng path cũng chưa tự giải quyết chính sách miền mở.**

Các HARD khác còn điều kiện ở môi trường, API đọc/load và quota đúng boundary. Việc ánh xạ lab cục bộ sang on-prem là giả định đã khai báo, không tự xác nhận khả năng triển khai sản xuất.

Đối chiếu: [JSON ca chính](results/PUBLIC-LAB-02.json), [JSON biến thể](results/PUBLIC-LAB-02-SOFT.json). Tìm `candidate_id: project_nessie` → assessment `R-I10-branching` → `trace.cases` để thấy cả path có claim và trường hợp chưa được bao phủ.

## Số liệu biến thể SOFT

| Ứng viên | Khoảng điểm | Credit đứng đầu / toàn bộ kịch bản đã đánh giá | Regret cực đại quan sát |
|---|---|---|---|
| Apache Gravitino | [0, 1] | 9,40% | 1 |
| Apache Polaris | [0, 1] | 8,37% | 1 |
| AWS Glue Data Catalog | [0, 1] | 6,77% | 1 |
| Hive Metastore | [0, 1] | 3,60% | 1 |
| Project Nessie | [0, 1] | 6,50% | 1 |
| Unity Catalog Databricks | [0, 1] | 6,70% | 1 |
| Unity Catalog OSS | [0, 1] | 5,27% | 1 |

Tỷ lệ này là credit đồng hạng theo completion giả định, **không phải xác suất catalog phù hợp ngoài thực tế**. Có 53,4% kịch bản không có ai đáp ứng HARD đã điền, nên tổng credit đứng đầu không cộng thành 100%. Gravitino có credit cao nhất ở mẫu này nhưng không trở thành khuyến nghị: cả bảy vẫn conditional và các khoảng điểm trùng nhau hoàn toàn. Regret được ghi là cực đại quan sát với cận trên riêng trong JSON; không gọi giá trị lấy mẫu là cực đại đã chứng minh.

## Giới hạn bao phủ workload

Cả hai nguồn có thao tác ghi; nhưng với I05 = `one`, mapping hiện chỉ giữ bối cảnh, trong khi I02 sinh yêu cầu engine `read`. Requirements thực tế chưa buộc chứng minh đường ghi Spark cho toàn workload này. Vì thế không được viết rằng kết quả đã xác nhận mọi thao tác ETL/ingestion của bài gốc.

Trace có tham chiếu requirement/claim hợp lệ về cấu trúc; điều này chưa kiểm chứng độ đúng thực tế của claim draft. Các nguồn hướng dẫn không phải đánh giá độc lập của chuyên gia và không cung cấp xếp hạng đối với toàn bộ bảy ứng viên.

## Cách đưa vào luận văn/báo cáo

Có thể báo: đã chuyển hai mục tiêu có nguồn thành input có provenance; pipeline ánh xạ đúng các nhánh quyền/credential/branching; khi thiếu thông tin hoặc chưa khép miền qualifier, hệ thống giữ kết luận có điều kiện và giải thích lý do; phép đổi rank tạo chuyển HARD → SOFT đúng thiết kế.

Chưa thể báo: hệ thống tìm ra catalog tối ưu, đạt accuracy trên hai bài toán, hoặc xác nhận phương án tham chiếu đã đạt mọi yêu cầu. Kết quả hiện tại chỉ ra giới hạn thu thập/ngữ nghĩa/path của MVP, không chỉ vấn đề thiếu số lượng case. Không dùng hai ca này để điều chỉnh rồi gọi lại là tập kiểm tra độc lập.

Trước vòng thực nghiệm đánh giá chất lượng khuyến nghị, cần người dùng quyết định chính sách xác nhận API/path ở Lớp 2–3; cách chuyển storage đã biết và kiểm chứng đường đọc/ghi/enforcement; sau đó kiểm chứng claim và quota đúng scope. Đây là đề xuất vòng sau, **chưa được tự áp dụng trong đợt nghiên cứu này**. Tăng số mẫu hoặc đổi weight không tự khắc phục những giới hạn trên.
