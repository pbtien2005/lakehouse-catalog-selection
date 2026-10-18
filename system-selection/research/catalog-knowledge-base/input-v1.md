# Bộ input v1 do người dùng chốt

Ngày: **17/10/2026**. Người điền chính: **architect / người ra quyết định**.

**Phạm vi đã chốt:** bộ câu hỏi trong mục 1, theo thông điệp mới nhất của người dùng. Riêng câu streaming vẫn có ghi chú phân vân, nên chưa coi việc giữ/bỏ hoặc bộ đáp án của câu này đã được xác nhận. Các quy ước ở mục 2–4 là đề xuất triển khai và diễn giải; không phải các câu hỏi mới được người dùng duyệt.

Tài liệu này là mốc phạm vi input hiện hành. [Nghiên cứu trước](user-input-design.md) được giữ làm tài liệu tham khảo, không dùng để tự bổ sung trường vào bộ hỏi đã chốt.

## 1. Câu hỏi và lựa chọn đã nhận

| ID | Câu hỏi | Lựa chọn người dùng chốt |
|---|---|---|
| I01 | Nơi chạy chính? | AWS / Azure / GCP / On-prem / Đa cloud |
| I02 | Engine truy vấn? | Spark / Trino-Presto / Flink / Snowflake / Databricks / Dremio / StarRocks-Doris / DuckDB / Khác |
| I03 | Table format? | Iceberg / Delta / Hudi / Chưa chọn / Hỗn hợp |
| I04 | Số bảng? | <100 / 100–1.000 / 1.000–10.000 / >10.000 |
| I05 | Số engine cùng ghi một bảng? | 1 / 2–3 / >3 |
| I06 | Có ghi streaming vào bảng không? | **Còn phân vân về việc giữ/bỏ; người dùng chưa chốt lựa chọn trả lời** |
| I07 | Cần phân quyền mức nào? | Cấp bảng / Cấp cột-hàng / Chưa rõ |
| I08 | Cần cấp quyền động (credential vending) cho engine ngoài? | Có / Không / Chưa biết |
| I09 | Hợp đồng/nền tảng đã gắn bó? | Databricks / Snowflake / AWS-native / Không |
| I10 | Nhu cầu đặc thù; mỗi mục có bắt buộc/nice-to-have | Thử nghiệm dữ liệu trên nhánh riêng rồi mới đưa vào bản chính; cập nhật nhiều bảng hoặc tất cả thành công hoặc tất cả thất bại; quản lý chung metadata từ nhiều catalog/nguồn qua một lớp thống nhất; không có nhu cầu nào trong số này |

## 2. Quy ước giao diện đề xuất, giữ nguyên phạm vi

- I02 nên cho chọn nhiều engine. Nhãn Trino-Presto và StarRocks-Doris được giữ đúng bản chốt; khi tri thức khác nhau giữa hai sản phẩm, chỉ kết luận phần được xác minh hoặc làm rõ thành viên nhóm. Không tự coi hai công nghệ có cùng support matrix.
- I03 = Hỗn hợp chỉ cho biết có nhiều format; không mặc định là cần cả Iceberg, Delta và Hudi. Cần giữ kết quả có điều kiện nếu chưa biết tổ hợp thực tế. I03 = Chưa chọn không được chuyển thành yêu cầu hỗ trợ mọi format.
- I04 có điểm giao tại 1.000. Đề xuất khoảng không chồng lấn: **<100 / 100–999 / 1.000–10.000 / >10.000**. Cách này giữ mốc >10.000 trong bản chốt, chỉ tách lại biên dưới của nhóm thứ ba.
- I05 nên ghi rõ trong hướng dẫn: số engine **ghi đồng thời vào cùng một bảng**. Đây là số engine, không phải số job/writer. Nếu một engine chạy nhiều job thì không tự suy concurrency = 1. Không tự diễn giải trường bỏ trống là một engine.
- I09 có thể chọn nhiều nền tảng khi tổ chức đã gắn bó với nhiều bên; “Không” loại trừ các mục còn lại. Đây là đề xuất cardinality, chưa phải lựa chọn được người dùng xác nhận riêng.
- I10 cho chọn nhiều nhu cầu cụ thể, mỗi nhu cầu được chọn có mức **bắt buộc** hoặc **nice-to-have**. “Không có nhu cầu nào” loại trừ ba nhu cầu cụ thể. Chưa đánh dấu mức không được mặc định là nice-to-have; chưa chọn gì khác với đã xác nhận không có nhu cầu.
- “Chưa biết” không được tự ánh xạ thành “Không”. Những câu chưa có lựa chọn này trong bản chốt không được hệ thống tự điền một đáp án thuận lợi khi người dùng bỏ qua.

## 3. Làm rõ streaming và đề xuất xử lý I06

**Có thể ghi streaming vào bảng lakehouse thông qua engine/connector phù hợp.** Catalog tham gia đường quản lý metadata/commit; không cần tự là hệ thống xử lý luồng mới tham gia được workload này. Tương thích và bảo đảm cụ thể phải đánh giá theo engine, connector, format, catalog và phiên bản.

Căn cứ đã kiểm tra ngày 17/10/2026:

1. Apache Iceberg có mục **Streaming Writes**, ví dụ Spark `writeStream` ghi vào bảng; mô tả append/complete theo micro-batch. Trang cũng phân biệt với Spark continuous processing mà Iceberg không hỗ trợ. Streaming writes có thể làm tăng tốc độ tạo phiên bản bảng và nhu cầu bảo trì metadata. [Spark Structured Streaming — Apache Iceberg](https://iceberg.apache.org/docs/latest/spark-structured-streaming/)
2. Hướng dẫn Polaris–Flink đăng ký REST catalog, bật checkpoint và ghi dữ liệu; ghi chú visibility sau checkpoint commit. Đây là bằng chứng tài liệu về đường tích hợp minh họa, không phải benchmark hoặc xác nhận mọi workload streaming với Polaris. [Polaris và Flink](https://polaris.apache.org/guides/flink/)

**Đề xuất:** giữ I06 như thông tin workload với lựa chọn **Không / Có / Chưa biết**. Đây vẫn là đề xuất, không ghi vào danh sách đáp án đã duyệt. Không dùng một thuộc tính đơn lẻ `catalog.supports_streaming` để lọc cứng; chỉ phát sinh yêu cầu tích hợp tương ứng khi có bằng chứng phù hợp. Nếu KB hiện tại chưa có claim hoặc phép kiểm tra nào dùng I06, có thể để ngoài form v1; lý do là chưa khai thác được dữ liệu, không phải mọi catalog đều không hỗ trợ đường ghi streaming.

## 4. Hợp đồng sử dụng input trong suy luận

| Input | Cách dùng | Điều không được tự suy ra |
|---|---|---|
| I01 Môi trường | Kiểm tra bối cảnh khả dụng và điều kiện triển khai đã biết | AWS → chỉ chọn Glue; On-prem → tự động loại mọi catalog managed |
| I02 Engine | Tra tương thích từng engine đã chọn, giữ giới hạn nếu chưa rõ thao tác/phiên bản | Tất cả engine đều phải ghi; hai sản phẩm cùng nhãn có tính năng giống nhau |
| I03 Format | Kiểm tra format được yêu cầu; giữ bất định khi chưa chọn/hỗn hợp chưa rõ | Đăng ký được metadata → đọc/ghi đầy đủ; chưa chọn → hỗ trợ cả ba |
| I04 Số bảng | Bối cảnh quy mô; dùng bằng chứng tải cùng phạm vi nếu có | Một khoảng số bảng tự chứng minh hiệu năng hoặc tạo ngưỡng loại tùy ý |
| I05 Engine ghi | Kích hoạt kiểm tra interoperability và concurrent commit khi liên quan | Nhiều engine → cần multi-table transaction; một engine → một writer |
| I06 Streaming, nếu giữ | Bối cảnh workload, kiểm tra đường ghi/commit và giới hạn liên quan | Cộng điểm mặc định cho một catalog; streaming → cần giao dịch nhiều bảng |
| I07 Quyền | Tạo yêu cầu quyền đúng phạm vi, giữ UNKNOWN khi điểm thực thi chưa rõ | Catalog có policy metadata hoặc credential vending → đã enforce row/column qua mọi engine |
| I08 Vending | Có → kiểm tra cơ chế và tổ hợp engine/storage phù hợp; Không → không tạo yêu cầu vending | Không cần vending → không cần bảo mật storage; mọi cơ chế cấp quyền động đều là vending |
| I09 Gắn bó nền tảng | Bối cảnh/ưu tiên; chỉ lọc cứng khi điều khoản bắt buộc được xác nhận | Hợp đồng Databricks → Unity Catalog OSS có đủ tính năng managed; hợp đồng tự chứng minh một ứng viên thắng |
| I10 Đặc thù | Bắt buộc → điều kiện không bù trừ; nice-to-have → ưu tiên có giải thích | Đếm số nhu cầu được chọn để xếp hạng; nhánh một bảng → nhánh cả catalog; công bố nhiều bảng qua merge → đã chứng minh mọi yêu cầu transaction nguyên tử |

Không mặc định mọi câu hiện trạng là ràng buộc B. Không tạo trọng số cố định từ nice-to-have. Nếu còn thiếu phạm vi có thể thay đổi kết quả, trả shortlist/cần xác minh có lý do thay vì khẳng định tương thích hoặc xếp hạng chắc chắn.

Input v1 này không thu riêng thao tác đọc/ghi từng engine, storage cụ thể, mức dịch vụ hoặc năng lực vận hành. Đó là giới hạn của bằng chứng quyết định từ form; không phải lý do tự mở rộng bộ hỏi đã chốt. Kết quả phải phản ánh đúng giới hạn đó, đặc biệt khi chưa đủ điều kiện đánh giá để đề xuất production.

Chưa triển khai form, schema hoặc bộ luật trong lượt cập nhật này; chưa có đánh giá thực nghiệm.
