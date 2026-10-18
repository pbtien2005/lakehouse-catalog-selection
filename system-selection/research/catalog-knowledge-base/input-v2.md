# Input v2 — form MVP lựa chọn catalog

Ngày: **17/10/2026**. Người điền: **architect / người ra quyết định**. Thay [input v1](input-v1.md) làm nguồn cho mapping hiện hành. Người dùng đã đồng ý sửa theo nhận xét feedback; bản v1 được giữ làm lịch sử, không sửa dữ liệu cũ ngầm.

Registry ID máy đọc duy nhất: [form-v2-registry.json](form-v2-registry.json). Giữ mười mục và hai mức **bắt buộc / nice-to-have**. Không thêm tiêu chí dễ vận hành, tránh lock-in hoặc câu hỏi authentication. I06 chưa bật; I09 là thông tin tùy chọn.

## 1. Phạm vi hiển thị trước khi điền

> Hệ thống tìm catalog đáp ứng môi trường, engine và format bạn chọn. Mặc định đánh giá đọc dữ liệu và nạp metadata; số bảng tính trong một catalog. Nếu có nhiều engine ghi đồng thời, MVP kiểm tra cơ chế concurrent append ở cấp catalog. Các yêu cầu nhánh được xét ở cấp catalog; cập nhật nhiều bảng xét tính nguyên tử khi công bố metadata. Nice-to-have dùng trọng số thấp từ config và được gắn weight_defaulted. Các giả định này cũng xuất hiện trong kết quả.

Phạm vi này do hệ thống định nghĩa, không phải thông tin hệ thống tự suy rằng người dùng đã cung cấp. Cấu hình chi tiết nằm trong [profile MVP](layer-2-mvp-profile.json). Payload MVP chỉ có answers theo registry. I01–I03 cụ thể được coi là HARD khi cờ default_environment_facts_as_hard=true; reminder ghi “đã coi lựa chọn này là bắt buộc”. Đảo cờ thành false thì chỉ giữ context. Candidate bindings chỉ là trace, không được thực thi trong MVP.

## 2. Bộ câu hỏi hiện hành

| ID | Câu hỏi | Lựa chọn / điều khiển |
|---|---|---|
| I01 | Phương án catalog phải dùng được ở môi trường nào? | AWS / Azure / GCP / On-prem / Đa cloud; chọn một |
| I02 | Phương án catalog phải hỗ trợ các engine nào? | Spark / Trino / Presto / Flink / Snowflake / Databricks / Dremio / StarRocks / Doris / DuckDB / Khác; chọn nhiều |
| I03 | Phương án catalog phải hỗ trợ table format nào? | Iceberg / Delta / Hudi / Chưa chọn / Hỗn hợp; chọn một |
| I04 | Số bảng dự kiến trong một catalog? | <100 / 100–999 / 1.000–10.000 / >10.000; chọn một |
| I05 | Số engine có thể ghi đồng thời vào cùng một bảng? | 1 / 2–3 / >3; chọn một |
| I06 | Có ghi streaming vào bảng không? | Giữ nhánh dự thảo, chưa hiển thị; Không / Có / Chưa biết chưa được bật |
| I07 | Cần phân quyền đọc dữ liệu tại catalog ở mức nào? | Không có yêu cầu phân quyền tại catalog / Cấp bảng / Cấp cột / Cấp hàng / Cả cấp cột và hàng / Chưa rõ; chọn một |
| I08 | Cần credential vending cho engine ngoài? | Có / Không / Chưa biết; chọn một |
| I09 | Hợp đồng/nền tảng đã gắn bó? | Databricks / Snowflake / AWS-native / Không; chọn nhiều, “Không” loại trừ các lựa chọn khác; mục tùy chọn |
| I10 | Nhu cầu đặc thù | Ba nhu cầu dưới đây, chọn nhiều; mỗi nhu cầu được chọn có bắt buộc hoặc nice-to-have. Không có nhu cầu nào loại trừ các nhu cầu cụ thể |

Ba nhu cầu I10:

- Thử nghiệm trên nhánh catalog riêng, ghi cô lập rồi công bố vào bản chính.
- Cập nhật metadata nhiều bảng: hoặc tất cả được công bố, hoặc không bảng nào được công bố trong thao tác đó.
- Quản lý/đọc metadata từ nhiều catalog hoặc nguồn qua một lớp thống nhất.

## 3. Diễn giải và giới hạn

- **I01–I03 là yêu cầu hỗ trợ** khi cờ HARD mặc định được bật. Một format cụ thể nghĩa là từng engine được chọn phải đọc được format đó theo profile. Không coi engine đọc là engine ghi. MVP chỉ nhận payload form; không nhận workload riêng hoặc tự nhân toàn bộ engine với nhiều format.
- **Chưa chọn format:** giữ unresolved, không tạo HARD về format và không tự chọn một format để làm ứng viên đạt. **Hỗn hợp**, đa cloud và engine Khác giữ unresolved, không tạo HARD trực tiếp từ những đáp án này. Không coi đa cloud là cả ba cloud hoặc tự đặt tên engine.
- **I04:** 1.000 và 10.000 cùng thuộc nhóm 1.000–10.000; các khoảng không giao nhau hoặc bỏ sót số nguyên không âm. Giữ khoảng, không tự lấy trung điểm; >10.000 có cận trên mở.
- **I05:** từ hai engine kích hoạt kiểm tra concurrent append cấp catalog. Chưa chứng minh MERGE/overwrite hoặc mọi engine ghi đều tương thích. Một engine có thể có nhiều job; không dùng đáp án 1 làm bằng chứng không có concurrency.
- **I07:** Cả cấp cột và hàng nghĩa là cần cả hai. Không có yêu cầu tại catalog không có nghĩa bỏ bảo mật ở lớp khác.
- **I08:** Có là yêu cầu bắt buộc. Storage chưa rõ chỉ làm kết luận vending có điều kiện; không suy AWS thành S3.
- **I09:** chỉ tạo bối cảnh/nhắc rà soát, không đổi weight hoặc loại ứng viên. Không bắt trả lời để có kết quả.
- **I10:** thiếu rank được báo lỗi. Mục không chọn không sinh yêu cầu đang hoạt động; không diễn giải thành kết luận vĩnh viễn rằng tổ chức không bao giờ cần tính năng đó.
- Giữ riêng chưa trả lời, chưa biết, chưa quyết định và không áp dụng có lý do trong dữ liệu. UI không cần hiển thị toàn bộ trạng thái nội bộ.

## 4. Chuyển dữ liệu từ v1

Không tự chuyển `trino_presto`, `starrocks_doris`, `100_to_1000` hoặc `column_row` sang đáp án mới. Các giá trị này cần chọn lại vì có thể đổi nghĩa. Giữ raw answers và revision ban đầu; câu trả lời hợp lệ của form v2 được đánh giá theo profile v2.

Đã có registry chung, payload UI theo ID và runtime Lớp 2. Luồng `run_case` đã nối suy luận xuyên suốt với cả bảy scope thật; xem [báo cáo MVP](../catalog-reasoner-mvp/outputs/mvp/final-report.md). I06 vẫn bất hoạt theo phạm vi đã chốt.
