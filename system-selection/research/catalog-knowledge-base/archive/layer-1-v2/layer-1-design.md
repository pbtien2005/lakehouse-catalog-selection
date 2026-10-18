# Thiết kế lớp 1 v2 — bản gọn cho prototype chọn catalog

Ngày: **17/10/2026**. Thay thế thiết kế sáu loại bản ghi trước đây. Bản cũ được giữ tại [archive v1](archive/layer-1-v1/layer-1-design.md); JSON cũ cũng đã được lưu ở cùng thư mục.

**Phạm vi:** thiết kế dữ liệu để chuẩn bị triển khai, theo [input đã chốt](input-v1.md). Chưa xây KB đầy đủ, schema hoặc bộ suy luận. Phạm vi nghiên cứu vẫn là sáu công nghệ hiện có; nhận xét gửi kèm nhắc lát cắt ba ứng viên nhưng chưa chỉ rõ tên, nên tài liệu không tự chọn ba công nghệ thay người dùng. Có thể biên soạn một tập con trước.

## 1. Đánh giá lại và quyết định sửa

Thiết kế cũ đúng về tách form, phạm vi và bằng chứng, nhưng đưa chi tiết triển khai và cơ chế quản lý dữ liệu vào quá sớm. Đặc biệt, khóa cấu hình SAS token là ví dụ sai trọng tâm: nó minh họa schema phức tạp mà không trực tiếp giúp chọn catalog với bộ input hiện tại.

| Nội dung nhận xét | Quyết định |
|---|---|
| Bỏ `integration.client_property_keys` và hai claim về hậu tố token | Đồng ý; bỏ khỏi KB quyết định hiện hành. Nội dung cũ còn trong archive |
| Bỏ bộ khớp `version_range`, `release_line`, `scheme` | Đồng ý cho v2; chỉ so khớp các giá trị phân loại bằng nhau |
| Gộp nguồn và bằng chứng vào claim | Đồng ý; giữ mảng `evidence`, không cần hai bảng riêng |
| Giảm author/review/revision/supports | Đồng ý; claim mặc định `status: draft`, dùng revision chung của bộ dữ liệu |
| Release là chuỗi trên scope | Đồng ý; dịch vụ không có release công khai dùng ngày `as_of`, không giả phiên bản |
| Thêm mức đáp ứng | Giữ, nhưng định nghĩa theo từng property; không ép mọi property có mức partial |
| Đặt `form_question` và `depends_on_form` trong property | Không áp dụng; mapping vẫn ở lớp 2, bảng truy vết đặt trong tài liệu thiết kế |
| Cloud tự xác định storage | Không áp dụng; nơi chạy engine không xác định duy nhất nơi lưu dữ liệu |
| Chưa biết storage thì lấy min–max các claim đã có | Chỉ đúng khi miền khả dĩ được xác định và bao phủ; thiếu claim vẫn phải tính là unknown |
| Bỏ qua kiểm chứng dữ liệu | Có thể hoãn lab/duyệt sâu trong prototype; không biến giả định dữ liệu đúng thành kết quả đã kiểm chứng |

V2 không phải bản sao phẳng của schema production, cũng không mặc định v1 là schema đích phải thực hiện sau này. Chỉ mở rộng lại khi có nhu cầu và dữ liệu cụ thể.

## 2. Cấu trúc mới: ba collection và manifest

```text
layer1.json
  manifest       Mục đích, revision, trạng thái và giới hạn bộ dữ liệu
  scopes[]       Catalog/edition/cách vận hành/release đang được mô tả
  properties[]   Thuộc tính dùng để lựa chọn và định nghĩa các mức
  claims[]       Mức kỹ thuật + điều kiện + bằng chứng ngay trong bản ghi
```

Một file đủ cho lát cắt ban đầu. Khi khó biên soạn vì file dài, có thể tách claims theo catalog mà không đổi mô hình. Chưa cần DB, graph, resolver tổng quát hoặc thư mục schema phức tạp.

### Scope

Trường tối thiểu: `id`, `catalog_id`, `name`, `edition`, `deployment_mode`, `release`. Dịch vụ thay `release` bằng `as_of` và ghi provider/region khi cần.

Scope giúp không trộn OSS với managed hoặc các release không tương thích. Một scope tham chiếu chưa là bản thiết kế triển khai đầy đủ. Lớp 3 chỉ kết hợp các claim trong cùng scope; nếu có scope thay thế, đánh giá riêng rồi mới gom theo catalog. Không ghép các điều kiện loại trừ nhau trong cùng scope.

Cùng scope là điều kiện cần, chưa đủ chứng minh mọi đường tích hợp cùng hoạt động. Nếu chỉ biết từng khả năng riêng lẻ mà chưa có cơ sở cho tổ hợp người dùng yêu cầu, giữ kết quả có điều kiện; bản gọn không tự tạo bảo đảm tương thích kết hợp.

### Property

Trường: `id`, `definition`, `qualifiers`, `ordered_levels`, `rubric`, `interpretation_limits`.

- `qualifiers`: các chiều phải biết để hiểu claim, ví dụ engine, format, operation, storage, API. Chỉ dùng các chiều có tác động tới ý nghĩa.
- `ordered_levels`: các mức kỹ thuật có thứ tự, chẳng hạn `[none, full]` hoặc `[none, partial, full]`.
- `rubric`: điều kiện quan sát được cho từng mức. “Full” phải đầy đủ đối với hợp đồng thuộc tính cụ thể, không nghĩa là sản phẩm đầy đủ mọi khả năng.
- `unknown` là trạng thái thiếu tri thức, không nằm trong thang thứ tự và không là mức 0.

### Claim

Trường: `id`, `scope_id`, `property_id`, `qualifiers`, `level`, `note`, `limits`, `evidence`, `status`.

- `qualifiers` là object giá trị phân loại đơn giản, ví dụ `{"storage":"aws_s3","api":"iceberg_rest"}`. Không có ngôn ngữ điều kiện hoặc bộ so phiên bản.
- `evidence` là mảng phần tử có `kind`, `url` hoặc `path`, `locator`, `retrieved_at`; có thể thêm ghi chú ngắn về phạm vi nguồn.
- `status` mặc định `draft`. Trong lượt này chưa thiết kế workflow phê duyệt nhiều bước. Prototype dùng draft phải ghi rõ đây là dữ liệu đang biên soạn.
- Claim `partial` cần thêm `covered_parts` và `unmet_parts`, có căn cứ cho cả hai. Phần chưa rõ phải ghi là chưa rõ, không giả thành unmet.

Giữ dấu vết nguồn dù chỉ có vài chục claim. Một nguồn dùng nhiều lần vẫn là một nguồn, không tự trở thành nhiều xác nhận độc lập. `retrieved_at` là ngày đọc, không phải ngày chạy lab.

## 3. Danh sách 10 property khởi đầu

Đây là từ điển đề xuất để biên soạn thử, không phải tuyên bố đã có đủ dữ liệu cho cả sáu catalog hoặc đã chốt thang giá trị/trọng số của lớp 3.

| Property ID | Câu hỏi kỹ thuật cần trả lời | Qualifier cần có | Mức đề xuất |
|---|---|---|---|
| `deployment.environment` | Scope có được mô tả là triển khai/sử dụng được trong môi trường này không? | environment | none/full; thiếu căn cứ → unknown |
| `integration.engine_operation` | Engine làm được thao tác này trên format này qua đường tích hợp nào? | engine, format, operation, api | none/full/unknown; một claim cho một thao tác |
| `catalog.format_operation` | Catalog quản lý được đối tượng/thao tác metadata của format này không? | format, operation, api | none/full/unknown; không tự chứng minh engine đọc/ghi |
| `commit.concurrent_write` | Đường tích hợp có cơ chế commit ghi đồng thời theo hợp đồng đã nêu không? | api, operation, writer_topology | none/full/unknown; lưu cơ chế và giới hạn, không tự biến số writer thành điểm |
| `integration.streaming_write` | Có đường ghi streaming/micro-batch cụ thể được hỗ trợ không? | engine, format, api, mode | none/full/unknown; chỉ biên soạn nếu giữ I06 hoặc có mục đích rõ |
| `security.authorization` | Có thực thi quyền ở boundary/action này qua đường truy cập đã nêu không? | granularity, action, access_path | none/full/unknown; bảng/hàng/cột được đánh giá riêng |
| `storage.credential_vending` | Catalog có trả credential storage tạm thời, giới hạn theo quyền được phép không? | storage, api | none/full/unknown; không bao gồm row/column enforcement |
| `workflow.branching` | Workflow tạo nhánh, ghi cô lập rồi công bố có được hỗ trợ ở cấp đối tượng này không? | object_scope, api | none/partial/full/unknown theo rubric dưới |
| `transaction.multi_table_atomic` | Các cập nhật nhiều bảng có all-or-nothing trong failure boundary đã nêu không? | api, client_path, failure_boundary | none/full/unknown; branch publish không tự chứng minh transaction |
| `metadata.federation_operation` | Lớp thống nhất làm được thao tác metadata này với nguồn cụ thể không? | source_type, operation, api | none/full/unknown; không tự chứng minh transaction hay governance xuyên nguồn |

**Rubric chung cho property nhị phân:** full = nguồn chỉ rõ thực hiện được đúng hợp đồng và điều kiện của claim; none = nguồn/quan sát có căn cứ chỉ rõ không đáp ứng hợp đồng đó; unknown = chưa đủ cơ sở. Nếu có prerequisite như IAM hoặc connector, ghi rõ; có prerequisite không tự làm mức giảm xuống partial.

**Rubric `workflow.branching`:** hợp đồng tham chiếu gồm tạo nhánh, ghi cô lập và công bố thay đổi ở `object_scope` đã xác định. Full khi cả ba phần có căn cứ; partial khi có phần làm được và có phần được xác định không đáp ứng; none khi có căn cứ không hỗ trợ các thành phần của workflow nhánh trong phạm vi đó; chỉ biết tạo nhánh nhưng chưa biết công bố thế nào → unknown, giữ phần đã biết trong note. Khi biên soạn có thể thay đổi hợp đồng này bằng revision property, không âm thầm đổi nghĩa các claim cũ.

Các mức là mô tả kỹ thuật trong phạm vi. Không quy `none/partial/full` mặc định thành `0/0.5/1`, không dùng thứ tự làm bằng chứng về khoảng cách giá trị. Tài liệu phương pháp lựa chọn hiện có cũng phân biệt mức thứ bậc với hàm giá trị để cộng trọng số. [Phương pháp khi KB đầy đủ](complete-kb-selection-method.md#41-tách-phép-đo-khỏi-giá-trị), [MCA manual, phần value scales và weighting](https://assets.publishing.service.gov.uk/media/5a790545e5274a2acd18b975/1132618.pdf)

## 4. Những dữ liệu chưa đưa vào lõi

- Khóa cấu hình client, hậu tố token, endpoint setup và dependency lock: để trong tài liệu triển khai. Chỉ giữ giới hạn tương thích nào thực sự thay đổi quyết định chọn công nghệ.
- Số contributor, điểm sức khỏe dự án, score chi phí/vận hành và mức trưởng thành: chưa thêm property chỉ để đủ danh sách. Bổ sung khi có mục tiêu đánh giá và cách đo rõ.
- Quota, số bảng đã thử, goodput, giá niêm yết hoặc thời gian vận hành: có thể lưu ở bảng quan sát riêng khi cần; không ép thành mức full hoặc dùng số đã thử làm giới hạn tối đa.
- Giấy phép và support vẫn có thể là metadata tham khảo ở scope/tài liệu nguồn khi có căn cứ, nhưng chưa tạo điểm/tiêu chí mềm mới ngoài mục tiêu đã xác nhận.

## 5. Nối với bộ input mà không làm lớp 1 phụ thuộc form

| Input | Tri thức được tra | Điều còn thiếu/không được suy |
|---|---|---|
| I01 Môi trường | `deployment.environment` | AWS không xác định storage, cũng không bắt buộc chọn Glue |
| I02 Engine | `integration.engine_operation` | Nhóm Trino-Presto/StarRocks-Doris phải phân biệt khi dữ liệu khác; chưa biết thao tác không tự yêu cầu mọi engine ghi |
| I03 Format | Hai property integration/format | Hỗn hợp chưa rõ thành phần không tự là AND mọi format |
| I04 Số bảng | Bối cảnh; chỉ tra quan sát/quota nếu có | Chưa có evidence hiệu năng thì không sinh điểm quy mô hoặc ngưỡng loại |
| I05 Engine ghi | `commit.concurrent_write` + integration | Số engine không bằng số job đồng thời; không suy transaction nhiều bảng |
| I06 Streaming, nếu giữ | `integration.streaming_write` | Chỉ dùng đúng mode/path, không có cờ streaming chung cho sản phẩm |
| I07 Quyền | `security.authorization` | Phải rõ boundary; chưa rõ hàng/cột hoặc engine thì giữ kết quả có điều kiện |
| I08 Vending | `storage.credential_vending` | Form chưa thu storage; không tự ánh xạ cloud thành storage |
| I09 Nền tảng gắn bó | Bối cảnh yêu cầu + scope và integration liên quan | Hợp đồng không phải thuộc tính kỹ thuật của catalog; không tự thêm điểm thương hiệu |
| I10 Đặc thù | Ba property workflow/transaction/federation | Bắt buộc/nice-to-have và cách so sánh do lớp 2–3 quyết định |

Bảng này là tài liệu truy vết. Không đưa `form_question`, `depends_on_form`, weight hoặc hard/soft vào file facts. Một thông tin bối cảnh có thể chưa trực tiếp làm đổi thứ hạng; không bịa property để mọi đáp án đều được cộng điểm.

## 6. Quy ước tra cứu tối thiểu

1. Chọn `scope_id` và `property_id`; so bằng nhau các qualifier đã định nghĩa. Không có wildcard ngầm, không cần version evaluator.
2. Thiếu qualifier thiết yếu hoặc gặp tổ hợp chưa biểu diễn được → unknown/conditional; không dùng note như luật máy ngầm.
3. Không có claim phù hợp → unknown. Tài liệu không nhắc đến không đủ tạo claim none. Một test lỗi chưa rõ nguyên nhân cũng chưa chứng minh none.
4. Hai claim cùng scope/property/qualifiers nhưng khác kết luận → dừng kết luận tự động cho khóa đó, đánh dấu cần phân giải. V1 gọn xử lý thủ công; chưa cần graph nguồn phản bác hoặc conflict solver.
5. Không gom các claim có điều kiện không thể đồng thời áp dụng thành một hồ sơ thắng. Giữ nguyên ràng buộc scope và điều kiện; không tự nới yêu cầu để tạo kết quả.

### Khi chưa biết storage

- Nếu chưa xác định tập storage được phép, trả thiếu input/kết quả có điều kiện, không tự chọn một storage.
- Nếu lớp 2 đã xác định miền hữu hạn D, chỉ lấy mức thấp nhất–cao nhất khi dữ liệu bao phủ D hoặc đã giữ đầy đủ phần chưa biết.
- Ví dụ giả định cùng scope: S3=full, ADLS=none, D gồm hai mục đó → kết quả có thể từ none đến full. Đây là tập kết quả có điều kiện, không phải điểm trung bình.
- S3=full, ADLS chưa có claim → không được trả `[full,full]`. Với property nhị phân, mức của ADLS còn có thể none hoặc full; giữ unknown và khoảng bảo thủ nếu lớp 3 cần.
- Không dùng xác suất bằng nhau hoặc một tập storage do hệ thống tự chọn để gọi kết quả là độ tin cậy. Việc quy các mức sang giá trị số thuộc mô hình lớp 3.

## 7. Ví dụ mới và đường chuyển đổi

[JSON v2](layer-1-example.json) chứa một scope Polaris, hai property minh họa (vending và branching) và **một claim vending** có nguồn, trạng thái draft. Property branching chỉ minh họa rubric; chưa có claim không nghĩa Polaris không hỗ trợ. Đây không phải KB đầy đủ hoặc ma trận xếp hạng.

Nguồn Polaris mô tả cơ chế credential cho S3; claim full trong ví dụ chỉ nói về hợp đồng catalog trả credential ở scope/path đã nêu, không khẳng định mọi engine hoặc workload đã chạy thành công. [Polaris 1.7.0, AWS S3](https://polaris.apache.org/releases/1.7.0/vended-credentials/)

| V1 | V2 |
|---|---|
| catalogs + scopes | Thông tin catalog/edition/release gộp trong scopes |
| release_selector | release là chuỗi |
| Property cấu hình client | Bỏ khỏi KB quyết định |
| Qualifier match/scheme/range | Giá trị phân loại bằng nhau |
| Source + evidence + evidence_links | Evidence nhúng trong claim, có thể nhiều nguồn |
| review/revision từng claim | status draft + revision chung manifest |
| value boolean | level theo rubric của property; không đổi máy móc true→full nếu hợp đồng chưa đủ |

V2 **không tương thích nguyên trạng** với JSON cũ; bảng trên là quy tắc chuyển đổi, không phải lời hứa chỉ đổi tên trường là đủ. Bản gốc được lưu để đối chiếu.

## 8. Kiểm tra và bước triển khai kế tiếp

Kiểm tra tối thiểu khi biên soạn: JSON hợp lệ, ID/reference đúng, qualifier đúng danh mục, level thuộc property, partial có phần đáp ứng/không đáp ứng và evidence, không trùng khóa kết luận trái nhau, không có trọng số/ID form trong facts. Chưa cần framework validation hoặc workflow review riêng để bắt đầu điền mẫu.

Thứ tự: thống nhất 10 property/hợp đồng đang đề xuất → điền lát cắt nhỏ theo scope → thử tra cứu exact + unknown → nối mapping → lớp 3 áp điều kiện bắt buộc và mô hình ưu tiên. Nếu chưa chốt rubric/giá trị của lớp 3 thì vẫn xây được kho tri thức này, nhưng chưa có cơ sở gọi nhãn full là điểm phù hợp tối đa.

Việc sửa này là đánh giá thiết kế, không xác nhận dữ liệu sản phẩm hoàn chỉnh. Không mở rộng form, không tự chọn tập ba ứng viên và không thay phương pháp suy luận đã nghiên cứu.
