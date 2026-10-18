# Lớp 2 v1 — ánh xạ input thành yêu cầu lựa chọn catalog

Ngày: **17/10/2026**. Trạng thái: **nghiên cứu và đặc tả ánh xạ có cấu trúc; chưa có normalizer/runtime hoặc lớp 3**.

Căn cứ hiện hành: [input v1](input-v1.md), [từ điển lớp 1 v3](layer-1-properties.json), [phương pháp lựa chọn](complete-kb-selection-method.md). Người dùng đã xác nhận **“Giữ bộ input hiện tại”** trong lượt này. Không điền thêm claim catalog, không đổi từ điển lớp 1 và không tự chọn ba ứng viên.

## 1. Quyết định phạm vi đã chốt

| Điểm cần chốt | Xử lý trong lớp 2 hiện hành |
|---|---|
| Dễ vận hành/tránh lock-in | Không thêm tiêu chí hoặc câu hỏi mới |
| Streaming | Giữ nhánh dự thảo, mặc định chưa bật vì I06 còn phân vân trong input v1 |
| Authentication | Không thêm câu hỏi OAuth2/OIDC. Facts authentication vẫn giữ ở lớp 1; chỉ dùng khi là điều kiện của đường tích hợp cần xét |
| Nền tảng đã gắn bó | CONTEXT và nhắc rà soát; không tự tính migration cost, đổi weight hoặc loại ứng viên |
| Bậc của nhu cầu đặc thù | Giữ **bắt buộc/nice-to-have**; không tự thêm “quan trọng/không cần” thành bậc mới |
| Lớp 1 | Giữ schema và dữ liệu hiện tại; lớp 2 xác định thứ tự thu thập tiếp theo |

Các chi tiết chưa đủ trong form được giữ thành trạng thái cần làm rõ hoặc điều kiện kết luận. Chúng không tự biến thành câu hỏi mới trên UI. Context bổ sung có thể đến từ hồ sơ ca/việc làm rõ đã được người chịu trách nhiệm xác nhận. Không yêu cầu người dùng tự biết catalog hỗ trợ tính năng nào.

## 2. Đánh giá các quy tắc được đề xuất

| Đề xuất đầu vào | Kết luận cho hệ thống này |
|---|---|
| Làm mapping trước khi điền thêm lớp 1 | Đồng ý; giúp thu đúng lát cắt cần dùng |
| Fact môi trường luôn là HARD/min partial | Chỉ HARD nếu xác nhận phải giữ. Property deployment hiện là nhị phân none/full, không có partial |
| Unknown mở ra mọi giá trị | Chỉ khảo sát miền hữu hạn được khai báo, giữ ràng buộc kết hợp; không tự chọn đáp án thuận lợi hoặc gán xác suất đều |
| Unknown = không cần nhưng gắn cờ | Không dùng; giữ nhu cầu chưa rõ, khác với xác nhận không cần |
| Nhiều writer tự tăng trọng số concurrency | Không dùng; workload làm thay đổi phép kiểm tra kỹ thuật, chưa xác định mức đánh đổi của người dùng |
| High=3, low=1 | Chỉ là preset minh họa bất hoạt; không suy từ form v1 vốn chưa có nhãn high/important |
| Giới hạn 2–3 HARD | Không áp trần. Nhu cầu bắt buộc không được hạ bậc để đủ quota; phân biệt một nhu cầu với nhiều phép kiểm tra nguyên tử |
| On-prem + cloud platform là mâu thuẫn | Chưa đủ; có thể là hybrid hoặc cam kết thương mại khác boundary |
| On-prem vô hiệu managed | Không suy từ nhãn này; form hiện cũng không có tiêu chí managed để vô hiệu |
| Authentication không hỏi thì xóa khỏi KB | Không xóa; không chấm như sở thích mới, nhưng vẫn có thể là điều kiện kỹ thuật của access path |

Căn cứ phương pháp: DSS lựa chọn phần mềm có tiền lệ tách điều kiện bắt buộc và ưu tiên; bài Farshidi còn có ca nhiều Must Have, nên không cung cấp căn cứ cho một trần chung ba yêu cầu. Đây là tham khảo cấu trúc, không phải validation trên catalog. [Farshidi et al., 2018, phần yêu cầu và case study](https://slingerjansen.nl/wp-content/uploads/2018/05/a-decision-support-system-for-software-technology-selection.pdf)

MCA manual giải thích trọng số qua giá trị của khoảng cải thiện trên từng thang. Vì vậy 3:1 không tự là mức ưu tiên đo được, dù có thể dùng làm kịch bản cấu hình có nhãn. [MCA manual, §6.2, Step 5 — Weighting](https://assets.publishing.service.gov.uk/media/5a790545e5274a2acd18b975/1132618.pdf)

GOV.UK khuyến nghị cho phép “không biết” khi hợp lệ; cách giữ unknown riêng với “không cần” dưới đây là quyết định thiết kế cho miền này. [Designing good questions](https://www.gov.uk/service-manual/design/designing-good-questions)

## 3. Lớp 2 làm gì và không làm gì?

```text
Câu trả lời gốc + context đã xác nhận + policy revision
  → chuẩn hóa trạng thái/giá trị
  → phân biệt HARD / SOFT / CONTEXT / chưa phân loại
  → tham chiếu property và neo chấp nhận
  → giữ qualifier từ người dùng hoặc biến chờ candidate path
  → trả hồ sơ yêu cầu + phần chưa rõ + cảnh báo + trace
  → lớp 3 xét KB, tính khả thi và ưu tiên
```

- **HARD:** điều kiện người dùng thực sự yêu cầu, không bù bằng điểm khác.
- **SOFT:** mục tiêu ưu tiên; chưa có weight/utility thì giữ nhãn và đánh đổi.
- **CONTEXT:** môi trường, workload, hợp đồng; không tự có điểm hoặc quyền loại ứng viên.
- **Chưa rõ:** thiếu nhu cầu, rank, context hoặc nghĩa của đáp án; không phải IGNORE.
- **NO_REQUIREMENT:** chỉ khi có câu trả lời phủ định nhu cầu, như I08=Không hoặc I10 xác nhận không có nhu cầu đặc thù.

Form chưa hỏi “phải giữ môi trường/engine/format không”. I01–I03 được lưu bối cảnh và có thể sinh yêu cầu dự thảo. Chỉ kích hoạt HARD khi có xác nhận hiện có trong hồ sơ ca; không áp sẵn chỉ vì người dùng chọn một nhãn.

API/connector của một candidate không phải lúc nào cũng do người dùng phải nhập. Lớp 3 có thể tìm đường phù hợp trong KB. Ngược lại, storage đang chứa dữ liệu, thao tác thật của engine hoặc phạm vi workflow là thông tin của ca; thiếu thì không được hệ thống chọn thay chỉ để làm một catalog thắng.

## 4. Bảng ánh xạ toàn bộ form

JSON [mapping](layer-2-mapping.json) chứa đủ **10 mục và 43 nhánh đáp án**, gồm các đáp án dự kiến cho I06 đang bất hoạt.

| Input / loại | Đáp án và hiệu ứng | Property đích | Mức tối thiểu / unknown |
|---|---|---|---|
| **I01 Nơi chạy — environment fact** | AWS/Azure/GCP/On-prem → CONTEXT. Đa cloud → cần tập môi trường thực tế. Khi đã xác nhận phải giữ, sinh HARD | deployment.environment | HARD dùng full. Không biết tập môi trường thì giữ unresolved; đa cloud không tự là OR chọn một hoặc AND cả ba |
| **I02 Engine — engine fact** | Các tên đơn được chuẩn hóa; nhóm Trino-Presto/StarRocks-Doris và Khác cần nhận diện đúng. Khi phải giữ, sinh HARD theo từng workload binding | integration.engine_operation | Full cho từng thao tác cần thiết; thiếu thao tác/format liên kết thì needs_context; không tự gán write |
| **I03 Format — format fact** | Iceberg/Delta/Hudi được ghi riêng; Chưa chọn giữ not_decided; Hỗn hợp cần tập format và workload thật | catalog.format_operation; integration.engine_operation | Full theo thao tác đã xác định, chỉ HARD khi phải giữ. Không tự AND cả ba format |
| **I04 Số bảng — scale** | Giữ khoảng nguyên; đề xuất kiểm tra quota, workload. Không sinh weight | limits.quota; performance.observation | Không dùng min_level. Quota/observations phải đúng boundary/scenario; thiếu số đo là thiếu KB, không hỏi người dùng sản phẩm có đáp ứng không |
| **I05 Engine cùng ghi — scale** | 1, 2–3, >3 là số engine. Từ hai engine trở lên nhắc xác nhận ghi đồng thời, operation/topology | commit.concurrent_write; integration.engine_operation | Chỉ HARD/full khi concurrency là nhu cầu đã xác nhận. Không biết topology thì chưa kết luận; không tạo transaction nhiều bảng |
| **I06 Streaming — nhánh chưa bật** | Giữ thiết kế Có/Không/Chưa biết cho tương lai; hiện không tác động gate/weight | integration.streaming_write; performance.observation | Không có trường này không tạo lỗi thiếu input. Nếu bật sau này, phải có engine/format/mode/path |
| **I07 Phân quyền — required capability** | Cấp bảng → nhu cầu HARD. Cột-hàng → nhu cầu HARD nhưng tập cấp quyền còn cần xác định; Chưa rõ → unresolved_need | security.authorization | Full trên từng granularity/action/path thật. Không tự coi cột-hàng là bắt buộc cả hai |
| **I08 Vending — required capability** | Có → HARD; Không → NO_REQUIREMENT; Chưa biết → unresolved_need | storage.credential_vending | Full theo storage thực và API/path có bằng chứng. Không suy storage từ cloud, không bỏ yêu cầu khi storage thiếu |
| **I09 Nền tảng gắn bó — context** | Databricks/Snowflake/AWS-native → lưu bối cảnh và nhắc rà soát; Không → không có cam kết được khai báo | Không tạo property năng lực mới; tham chiếu scope/integration/migration/cost chỉ khi có yêu cầu liên quan sau này | Không min_level, không weight, không loại. Unknown chỉ là chưa biết cam kết |
| **I10 Đặc thù — ranked group** | Branching / atomic nhiều bảng / federation; từng mục có bắt buộc hoặc nice-to-have. Không có nhu cầu nào loại trừ các mục cụ thể | workflow.branching; transaction.multi_table_atomic; metadata.federation_operation | Bắt buộc → HARD/full. Nice → SOFT, weight chưa đặt. Thiếu rank → needs_rank, không mặc định nice |

### Neo cho ba nhu cầu đặc thù

- **Branching:** tạo nhánh, ghi cô lập và công bố thay đổi tại scope cần dùng. Full đáp ứng cả hợp đồng; partial chỉ dùng khi biết phần nào thực sự không đáp ứng. Bắt buộc toàn workflow không được pass bằng partial.
- **Atomic nhiều bảng:** không công bố trạng thái chỉ một phần bảng được commit, qua client/API và failure boundary đã xác nhận. Không đòi “không có orphan file” nếu yêu cầu chỉ về atomic visibility. Branch publish có thể là một đường thực hiện nếu có bằng chứng cho cùng hợp đồng; không tự coi tương đương.
- **Federation:** từng loại nguồn và từng thao tác được yêu cầu làm được qua lớp thống nhất; không yêu cầu hỗ trợ mọi nguồn trên thị trường hoặc tự suy governance/transaction xuyên nguồn.

### Neo cho năm mục cắt lát đầu tiên

Thứ tự người dùng đề xuất là **I01, I02, I03, I08, I07**, không phải I01–I05. Tất cả các property hỗ trợ trong lát cắt này có rubric nhị phân, nên ngưỡng HARD là **full**. Điều kiện chi tiết, nguồn của từng qualifier và giới hạn nằm tại [anchors](layer-2-anchors.json).

Không tự đặt một profile “mọi engine phải ghi” hoặc “mọi catalog phải create/drop”. Với các thao tác chưa có, yêu cầu dự thảo vẫn được giữ, nhưng chưa gọi là đã đặc tả đủ để kết luận phù hợp.

## 5. Khoảng số bảng và qualifier

Giữ nguyên khoảng của form hiện hành: <100 → [0,99]; 100–1.000 → [100,1000]; 1.000–10.000 → [1000,10000]; >10.000 → [10001,∞). Hai khoảng cùng chứa 1.000 là vấn đề nhãn của form đã có, không tự sửa ngầm thành 999 trong lớp 2.

Với quota Q và khoảng [L,U]:
- Q < L: toàn khoảng vượt quota, nếu quota/boundary có bằng chứng phù hợp.
- U hữu hạn và Q ≥ U: toàn khoảng trong quota; điều này chưa chứng minh SLO hiệu năng.
- Các trường hợp còn lại: có điều kiện, không lấy trung điểm để tự quyết.
- Không có quota hoặc đang dùng số bảng từng thử thay quota: chưa đủ cơ sở.

Mỗi qualifier được phân biệt nguồn: **form**, **context đã xác nhận**, **candidate path** hoặc **hằng số có định nghĩa**. API là biến chờ layer 3 không đồng nghĩa thiếu thông tin người dùng. Các engine có thể dùng API khác nhau, nhưng phải cùng một catalog state/scope tương thích. Không bắt mọi engine dùng chung một chuỗi API.

Lớp 3 phải tìm một tổ hợp đường tương thích giữa engine, metadata, storage delegation và phân quyền. Các tên đường logic như `spark_data_path` phải được gắn với đường thực của candidate. Các claim full rời rạc trên những đường không ghép được với nhau chưa chứng minh một phương án khả thi.

## 6. Trạng thái chưa biết và cảnh báo

Tách: chưa trả lời, người dùng chưa biết, chưa quyết định, không cần và ngoài phạm vi có lý do. Không sinh phân phối xác suất hoặc tự bỏ yêu cầu từ những trạng thái này.

Không phải mọi giá trị chưa rõ đều chặn đánh giá: I09 chỉ là context nên không tự chặn readiness; I06 bất hoạt không tạo việc làm rõ khi vắng hoặc unknown. Phần chưa rõ ảnh hưởng điều kiện bắt buộc mới làm kết luận về tính phù hợp có điều kiện.

Ba nguồn bất định khác nhau:
1. **Thiếu nhu cầu/rank:** người dùng hoặc hồ sơ ca cần làm rõ.
2. **Thiếu context:** cần xác định storage, operation, tập nguồn hoặc workflow scope.
3. **Thiếu khả năng sản phẩm/bằng chứng:** lớp 3 trả UNKNOWN và kho tri thức cần nghiên cứu; không bắt người dùng tự biết tính năng catalog.

Mapping có 11 quy tắc, không sửa câu trả lời:
- Hybrid on-prem + nền tảng cloud: nhắc làm rõ, không tự báo mâu thuẫn.
- None đi kèm lựa chọn cụ thể, chọn nhiều cho trường đơn, rank thiếu/ngoài phiên bản: input cần sửa, giữ raw answers.
- Vending có nhưng storage thiếu; nhóm fine-grained chưa rõ; engine/format nhóm chưa rõ; đa cloud chưa có tập cụ thể: needs_context.
- Nhiều engine ghi: nhắc xác nhận concurrency, không đổi ưu tiên.
- Chỉ gọi là xung đột trực tiếp khi context đã xác nhận vừa bắt buộc vừa cấm cùng một việc ở cùng boundary/thời điểm.

Form hiện không có tiêu chí “managed”, “lock-in” hoặc bậc “không cần concurrency”, nên không dựng luật cảnh báo như thể các trường đó đã tồn tại. “Không tìm được catalog phù hợp” thuộc chẩn đoán lớp 3, chưa chứng minh input tự mâu thuẫn.

## 7. Trọng số và số mục bắt buộc

[Policy riêng](layer-2-policy.json) đặt:
- Không tự đổi weight theo số bảng, số writer, streaming hoặc vendor commitment.
- Không có hard cap 2–3; không tự hạ bậc. Một nhu cầu có thể tách thành nhiều predicate, không bị đếm thành nhiều lợi ích.
- SOFT được chuyển tiếp với weight chưa đặt. Nếu chỉ có HARD, trả tập phù hợp/hòa thay vì tạo tiêu chí mới để ép ranking.
- Có preset minh họa **3:1** và equal-soft, nhưng **bất hoạt**. Muốn dùng cần chấp nhận preset, thang giá trị, tránh đếm trùng và đúng nhãn ưu tiên trong revision form. V1 hiện không có important/high.
- Chuẩn hóa chỉ trên các objective SOFT đang hoạt động sau khi mô hình giá trị/ưu tiên được chấp nhận. Không chuẩn hóa HARD chung với SOFT.

Giữ các preset trong config không đồng nghĩa đã xác nhận độ lớn đánh đổi. Nếu cần thử 2:1 hoặc 5:1 sau này, sửa config và gắn nhãn sensitivity; không thay sự thật lớp 1.

## 8. Danh sách property cần thu thập tiếp

[Property plan](layer-2-property-plan.json) phân loại đủ **37 property** đang có, không xóa/sửa lớp 1:

| Nhóm | Số property | Cách dùng |
|---|---:|---|
| Lát cắt năm mục ban đầu | 5 | deployment.environment; integration.engine_operation; catalog.format_operation; storage.credential_vending; security.authorization |
| Nhu cầu đặc thù khi được chọn | 3 | workflow.branching; transaction.multi_table_atomic; metadata.federation_operation |
| Workload có điều kiện | 2 | commit.concurrent_write; limits.quota |
| Performance chờ có target | 1 | performance.observation |
| Streaming đang bất hoạt | 1 | integration.streaming_write |
| Điều kiện của đường tích hợp | 9 | API, authentication, policy, storage lifecycle và commit guarantee; chỉ thu khi path cần |
| Giữ ngoài lát cắt hiện tại | 16 | Không xóa; chưa ưu tiên điền hoặc dùng làm tiêu chí tự động |

Có **12 property đích trực tiếp**, nhưng không điền cả 12 ngay. Lát cắt đầu tiên là năm property; phụ thuộc kỹ thuật chỉ bổ sung khi cần chứng minh đường đang xét. Việc một property không có câu hỏi riêng không khiến nó biến thành tiêu chí mới hoặc bị xóa khỏi từ điển miền.

I09 có vai trò lưu context/hợp đồng nên không cần bịa một property như “phù hợp Databricks”. Đây là ngoại lệ có lý do cho phép kiểm tra hai chiều: các input phải có hành động sử dụng rõ, không nhất thiết có một ô tính năng được cộng điểm.

## 9. Đầu ra chuẩn hóa và ví dụ

Đầu ra cho lớp 3 gồm:
- revision form/mapping/policy/dictionary;
- raw answers và normalized context;
- requirements có logical_need_id, source inputs, role, status, property, qualifier/candidate binding và anchor;
- objectives SOFT, weight còn trống nếu chưa xác nhận;
- unresolved, input issues, reminders và trace.

Ba trạng thái tiếp nhận: **ready_for_assessment**, **conditional_assessment_only**, **needs_input_correction**. Ready cho lớp 3 không nghĩa đã có catalog đạt yêu cầu. Lớp 2 không trả tên catalog đứng đầu.

[16 ca tham chiếu](layer-2-examples.json) minh họa:
- Lát cắt năm mục với context được khai báo rõ tạo tám predicate HARD, không vi phạm một trần giả định và không đếm thành tám mục tiêu SOFT.
- I08 Có nhưng storage thiếu vẫn giữ HARD đang needs_context; I08 Chưa biết khác I08 Không.
- Engine nhóm + format hỗn hợp không tự mở thành AND/OR có lợi cho một catalog.
- Khoảng số bảng cắt quota hoặc có upper vô hạn phải có điều kiện.
- Nhiều writer không đổi weight; on-prem + AWS-native chưa mâu thuẫn.
- Mandatory khác nice; thiếu rank/none cùng nhu cầu cụ thể là lỗi input, không sửa ngầm.
- Streaming vắng mặt khi chưa bật không sinh lỗi.
- Nhãn important chưa có trong form bị báo ngoài phiên bản.

Đây là **ca viết tay để làm oracle phát triển**, không phải output của một normalizer đã triển khai hoặc thử nghiệm trên sản phẩm thật. Các con số quota trong ví dụ là giả định, không phải giới hạn của catalog cụ thể.

## 10. Artifact và kiểm chứng

Các file JSON là đặc tả khai báo có cấu trúc, **chưa phải rule engine hay mã thực thi ánh xạ**. Dùng DMN làm tham khảo cách tách dữ liệu đầu vào và quyết định, nhưng không tuyên bố tuân thủ DMN hoặc yêu cầu thêm DMN runtime. [OMG DMN](https://www.omg.org/spec/DMN)

Kiểm tra cấu trúc có thể thực hiện ngay: đủ input/đáp án; property/anchor hợp lệ; ngưỡng thuộc đúng rubric; đủ qualifier binding; các preset bất hoạt; property plan bao phủ 37 mục; ví dụ tham chiếu đúng revision; không đổi hash lớp 1/input. Các ca tham chiếu chỉ trở thành kiểm thử hành vi khi có normalizer, không được gọi là đã pass engine trong giai đoạn này.

Đã chạy kiểm tra tĩnh các file hiện hành; [báo cáo kiểm tra](layer-2-validation.json) ghi riêng kết quả, số lượng và phạm vi. Hash của input v1 và bốn file lớp 1 giữ nguyên so với đầu lượt. Kiểm tra này không xác nhận khả năng sản phẩm và không chạy 16 ca qua normalizer.

Thứ tự tiếp theo: review hợp đồng mapping/neo → thu đúng claim của lát cắt → viết normalizer và dùng các ca tham chiếu làm test → lớp 3 đánh giá bằng chứng, tính khả thi, mô hình giá trị và giải thích. Chưa có ba ứng viên cụ thể được chốt; mapping dùng chung cho tập scope được chọn sau.

