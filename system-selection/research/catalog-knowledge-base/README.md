# Nghiên cứu cơ sở tri thức cho web lựa chọn công nghệ catalog

**Cập nhật 18/10/2026:** có [15 claim bổ sung có nguồn và hai profile tương thích](evidence-review-2026-10-18.md), [input v3](input-v3.md) và [thực nghiệm chất lượng](../catalog-reasoner-mvp/experiments/quality-upgrade-2026-10-18/README.md). Bản `layer-1-data.json` gốc không đổi; form v3 dùng overlay phiên bản riêng. Profile là bằng chứng cho đường thực hiện của một catalog, không phải chứng nhận hạ tầng hiện hữu đã chạy đúng. Các mốc và đề xuất cũ bên dưới được giữ làm lịch sử.

**Cập nhật 17/10/2026 — đã có bộ dữ liệu lớp 1 từ nguồn chính thức cho 7 công nghệ.** Bắt đầu tại [ghi chú dữ liệu và phạm vi](layer-1-research-notes.md), [JSON facts](layer-1-data.json), [61 nguồn chính thức](layer-1-sources.md) và [bảng coverage 37 thuộc tính × 7 scope](layer-1-coverage.md). Có 203 claim: 173 có kết luận theo phạm vi, 30 unknown/null; tất cả còn draft và chưa kiểm chứng runtime. Unity Catalog OSS và Unity Catalog trên Databricks được tách riêng theo danh sách người dùng yêu cầu. [Báo cáo kiểm tra dữ liệu](layer-1-data-validation.json) và [script](validate-layer-1-data.py) đi kèm. Các phần nghiên cứu đề xuất phía dưới giữ mốc lịch sử 15/10/2026.

Ngày: **15/10/2026**. Trạng thái: **đề xuất thiết kế từ tổng quan có chọn lọc; chưa xây cơ sở tri thức hoặc chạy đánh giá prototype**.

## 1. Mục tiêu và thông tin đã xác nhận

Người dùng muốn xây website tự động hóa phương pháp lựa chọn catalog đã nghiên cứu. **Đối tượng đầu ra là công nghệ catalog được đề xuất**, kèm lý do và điều kiện ảnh hưởng đến khuyến nghị. Phiên bản hoặc đường tích hợp chỉ là phạm vi của bằng chứng khi cần; không biến đầu ra thành thiết kế triển khai.

Thông tin người dùng bổ sung trong lượt này:

- Phục vụ đồ án/nghiên cứu, có prototype để kiểm chứng.
- Người dùng trả lời bộ câu hỏi hoặc điền form có cấu trúc.
- Dùng báo cáo nghiên cứu công nghệ đã có làm nguồn xây cơ sở tri thức.
- LLM có thể không dùng. Nếu dùng, vai trò dự kiến là diễn đạt lại yêu cầu và viết giải thích.

Phạm vi ban đầu kế thừa sáu công nghệ của nghiên cứu hiện có: Hive Metastore, AWS Glue Data Catalog, Apache Polaris, Project Nessie, Apache Gravitino, Unity Catalog OSS. Cần người dùng xác nhận nếu thay đổi phạm vi. Chưa biết thời hạn, người duyệt, bộ ca tham chiếu và mức chấp nhận đánh đổi.

Liên quan: [framework v2](../catalog-selection-framework/README.md), [biểu mẫu](../catalog-selection-framework/templates.md), [nghiên cứu phương pháp đã có](../catalog-method-review/README.md). Tài liệu này bổ sung hướng xây tri thức; không sửa hoặc thay framework hiện hành.

Luồng xử lý từ form đến kết quả được đề xuất riêng tại [Logic lựa chọn catalog](decision-flow.md), gồm sàng lọc, xử lý thiếu bằng chứng, so sánh ưu tiên, hỏi bổ sung và kiểm chứng.

Hướng nâng cấp thuật toán được nghiên cứu tại [Suy luận ưu tiên khi thông tin chưa đầy đủ](advanced-reasoning.md): ROR, minimax regret, hỏi tương tác, giải thích và thiết kế thực nghiệm đối chiếu.

Thiết kế input cho architect/người ra quyết định được đề xuất tại [Bộ câu hỏi và cách xử lý input](user-input-design.md): phân biệt hiện trạng với yêu cầu bắt buộc, câu hỏi theo nhánh, ưu tiên, dữ liệu chưa biết và bộ ca phát triển.

**Input hiện hành sau khi người dùng đồng ý sửa theo feedback ngày 17/10/2026** là [Input v2 cho MVP](input-v2.md): I01–I03 hỏi yêu cầu hỗ trợ, engine được tách riêng, khoảng số bảng không giao nhau và phân quyền có lựa chọn rõ ràng hơn. Mốc ban đầu giữ tại [Input v1](input-v1.md). Streaming chưa bật; nền tảng gắn bó là bối cảnh tùy chọn.

Thiết kế lớp sự thật hiện hành là [Lớp 1 v3 — tri thức kỹ thuật catalog](layer-1-design.md), có 11 nhóm nội dung và [từ điển 37 thuộc tính](layer-1-properties.json), gồm table format, engine/API, authentication, authorization, storage, commit, versioning, federation và vận hành. Có [bộ khung biên soạn](layer-1-template.json), [JSON ví dụ v3](layer-1-example.json) và [bộ dữ liệu 7 công nghệ](layer-1-data.json). Dữ liệu gồm scopes và claims có evidence nhúng; mức hỗ trợ chỉ dùng cho capability, các mô tả/tập giá trị/số đo giữ kiểu riêng. Từ điển v3.1 bổ sung qualifier tùy chọn cho loại bảng và metadata representation. Bản trước được giữ tại [archive v1](archive/layer-1-v1/README.md) và [archive v2](archive/layer-1-v2/README.md). Bộ dữ liệu hiện có bằng chứng theo lát cắt và [khoảng trống công khai](layer-1-coverage.md), chưa là đánh giá đầy đủ mọi tổ hợp hoặc runtime validation.

**Lớp 2 v2 — Nhóm 1 đã có runtime** tại [thiết kế hiện hành](layer-2-design.md): [registry ID duy nhất](form-v2-registry.json), [mapping đủ 48 nhánh](layer-2-mapping.json), [config Lớp 2](layer-2-runtime-config.json), [policy](layer-2-policy.json), [profile](layer-2-mvp-profile.json) và [anchors](layer-2-anchors.json). I01–I03 cụ thể sinh HARD theo cờ config; đáp án tổng hợp giữ unresolved, không HARD. Nice-to-have lấy trọng số thấp từ config suy luận hiện có và gắn weight_defaulted. Người dùng chọn cả bảy scope thật. Candidate bindings chỉ là trace; không thực thi joint path resolver. [Runtime Python](../catalog-reasoner-mvp/catalog_reasoner/layer2.py), [kiểm tra/hash hiện tại](layer-2-validation.json) và [48 profile tổng hợp đã chạy qua Lớp 2](layer-2-examples.json). UI gửi ID từ registry và không còn evaluator fixture riêng; chưa nối Lớp 3. [Property-plan](layer-2-property-plan.json) và 25 property ngoài target trực tiếp giữ nguyên.

Trường hợp giả định KB chính xác và đầy đủ được nghiên cứu riêng tại [Phương pháp lựa chọn với KB đầy đủ](complete-kb-selection-method.md): mô hình yêu cầu kết hợp, thang giá trị/trọng số, điều kiện dùng Weighted Sum, xử lý xung đột và thiết kế kiểm chứng. Tám ví dụ toán học giả định có [script](complete-kb-checks.py) và [kết quả](complete-kb-check-results.json); chưa phải thực nghiệm chọn catalog.

## 2. Câu hỏi nghiên cứu

1. Cơ sở tri thức cần trả lời những câu hỏi nào để hỗ trợ chọn catalog?
2. Biểu diễn nào đủ diễn đạt điều kiện áp dụng, giới hạn, nguồn và dữ liệu chưa biết?
3. Chuyển báo cáo đã có thành tri thức kiểm tra được như thế nào?
4. Liên kết nhu cầu của người dùng với đặc tính catalog bằng quy tắc nào?
5. Đánh giá chất lượng tri thức và giá trị hỗ trợ lựa chọn bằng cách nào?

Tách ba quyết định: **biểu diễn tri thức**, **cơ chế lựa chọn**, **công nghệ lưu trữ**. Một mô hình khái niệm rõ không bắt buộc triển khai bằng OWL; knowledge graph không đồng nghĩa phải dùng một graph database cụ thể. Tương tự, cây câu hỏi là luồng thu thập yêu cầu, không tự thay thế kho sự thật và bằng chứng.

## 3. Căn cứ từ tài liệu

Đã kiểm tra 11 nguồn phương pháp/nghiên cứu/chuẩn, mức đọc khác nhau; xem [phiếu nguồn](sources.md). Đây là tổng quan tập trung, không phải systematic literature review. Tài liệu nền tảng cũ được giữ vì liên quan trực tiếp; có đối chiếu nghiên cứu năm 2025.

- Hệ khuyến nghị dựa trên ràng buộc phân biệt kiến thức về nhu cầu, sản phẩm và quan hệ đáp ứng nhu cầu. Cấu trúc này gần với đầu vào form và đầu ra công nghệ của đề tài. [Felfernig & Burke, 2008](https://doi.org/10.1145/1409540.1409544)
- DSS lựa chọn công nghệ phần mềm có tiền lệ dùng mô hình đặc tính, giá trị đặc tính và yêu cầu để sàng lọc. Việc kế thừa cấu trúc không buộc dùng cùng công thức tính điểm. [Farshidi et al., 2018](https://doi.org/10.1080/12460125.2018.1464821)
- Thiết kế mô hình nên bắt đầu từ các câu hỏi cần trả lời và được sửa qua các vòng thử. [Noy & McGuinness, 2001](https://protege.stanford.edu/publications/ontology_development/ontology101-noy-mcguinness.html)
- Cần tổ chức cả thu thập, mô hình hóa, đánh giá, tài liệu hóa và bảo trì; dựng schema chỉ là một phần công việc. [METHONTOLOGY, 1997](https://cdn.aaai.org/Symposia/Spring/1997/SS-97-06/SS97-06-005.pdf)
- Khi biểu diễn quan hệ phức tạp, thời gian và phạm vi đúng của thông tin cần được ghi rõ. [Hogan et al., 2021](https://arxiv.org/html/2003.02320)
- PySelect là nghiên cứu gần bài toán chọn phần mềm có dùng KG. Tuy nhiên, kết quả đối chiếu của chính bài chưa đủ để kết luận KG luôn vượt LLM; cũng chưa kiểm chứng cho catalog. [Farshidi et al., 2025, preprint v1](https://arxiv.org/html/2508.05693v1)

Những giải pháp bên dưới là **suy luận thiết kế cho đề tài này**, không phải kết luận đã được các bài báo xác nhận trên sáu catalog.

## 4. Các giải pháp đáng thử

Đây là ba cách tổ chức prototype có thể so sánh. Chúng có thể kết hợp và không phải các khái niệm loại trừ nhau.

| Giải pháp | Cách làm | Điều kiện phù hợp | Công sức và giới hạn dự kiến |
|---|---|---|---|
| **A. Tri thức có cấu trúc + quy tắc ràng buộc** | Định nghĩa tiêu chí; ghi mệnh đề và bằng chứng; form ánh xạ sang yêu cầu; quy tắc sàng lọc rồi phân tích ưu tiên | Tập công nghệ xác định; yêu cầu nhập bằng form; cần truy vết; đã có báo cáo | Cần biên soạn dữ liệu và kiểm tra mapping. Quan hệ nhiều chiều phải mô hình hóa rõ |
| **B. Ontology/KG + quy tắc** | Khai báo khái niệm và quan hệ; gắn ngữ cảnh; truy vấn quan hệ, suy diễn và đánh giá ràng buộc | Có câu hỏi thực sự cần phân cấp khái niệm hoặc truy vấn nhiều quan hệ dùng lại | Thêm công mô hình hóa và kiểm tra suy diễn. Chỉ chọn khi giải quyết được câu hỏi A xử lý khó |
| **C. Kho tài liệu + RAG + lớp kiểm tra ràng buộc** | Truy xuất đoạn báo cáo để trả lời; chuẩn hóa kết quả và kiểm tra trước khi khuyến nghị | Có nhu cầu hỏi đáp tự do, khám phá tài liệu | Cần đánh giá retrieval và độ bám nguồn; không có căn cứ mặc định rằng câu trả lời sinh ra tuân thủ mọi điều kiện bắt buộc |

**Đề xuất hiện tại: dùng A làm phương án chính, giữ B làm phương án đối chiếu nếu có nhu cầu quan hệ rõ.** Với form và phạm vi LLM người dùng đã chọn, C chưa giải quyết một nhu cầu trung tâm. Nghiên cứu RAG gốc kiểm chứng các tác vụ NLP, không cung cấp bảo đảm về quyết định lựa chọn catalog. [Lewis et al., 2020](https://arxiv.org/html/2005.11401)

Case-based reasoning chỉ nên khảo sát sâu khi có kho ca lựa chọn thực, đầu vào và kết quả đủ tin cậy. Báo cáo mô tả công nghệ hiện có chưa tự tạo thành kho ca đó. Quy tắc viết tay có thể dùng ngay mà không cần huấn luyện cây học máy. Cây câu hỏi vẫn có thể là giao diện của A hoặc B.

## 5. Mô hình khái niệm đề xuất cho A

Chưa chốt schema database. Trước hết cần định nghĩa sáu nhóm tri thức:

| Nhóm | Nội dung | Ví dụ về vai trò, không phải khẳng định sản phẩm |
|---|---|---|
| **Catalog** | Định danh công nghệ/edition, tên và phạm vi | Tránh trộn Unity Catalog OSS với sản phẩm thương mại |
| **Concept/criterion** | Định nghĩa đặc tính, kiểu giá trị, đơn vị, thao tác và cách kiểm tra | Phân biệt branching cấp bảng với branching cấp catalog |
| **Claim** | Một mệnh đề về khả năng hoặc giới hạn; giá trị; điều kiện và phạm vi | Khả năng hỗ trợ một thao tác qua một đường tích hợp |
| **Evidence** | Đoạn báo cáo, nguồn gốc, section, release/ngày; loại tài liệu hoặc test; giới hạn | Phân biệt documented support với runtime verification |
| **Requirement–capability mapping** | Nhu cầu nào cần những thuộc tính nào, ở mức tối thiểu nào; các điều kiện kết hợp | Một mục tiêu của người dùng có thể cần nhiều đặc tính đồng thời |
| **Decision rule** | Quy tắc kiểm tra bắt buộc, ưu tiên, thiếu thông tin và giải thích | Thiếu bằng chứng chấp nhận được cho điều kiện B → UNKNOWN |

Hồ sơ từng lần lựa chọn lưu riêng: câu trả lời form, yêu cầu đã chuẩn hóa, phiên bản tri thức/quy tắc đã dùng và kết quả. B/U/I thuộc bối cảnh lựa chọn, không phải nhãn cố định của catalog.

Trạng thái bằng chứng, trạng thái duyệt và kết quả đánh giá phải tách nhau:

- Mệnh đề có thể được nguồn ủng hộ, phản bác hoặc chưa phân giải.
- Bản ghi có thể đang nháp, được duyệt hoặc cần xem lại.
- PASS/FAIL/UNKNOWN/N/A là kết quả áp dụng yêu cầu cụ thể lên tri thức thích hợp.

Thiếu bản ghi không tự là bằng chứng không hỗ trợ. Hai nguồn khác phạm vi cần tách trước khi gọi là mâu thuẫn. Không ghép khả năng của các phiên bản/edition không tương thích để khẳng định một catalog đáp ứng đồng thời mọi yêu cầu. Chỉ ghi chi tiết phiên bản hoặc tích hợp ở mức cần để giải thích tính hợp lệ của khuyến nghị.

Có thể tham khảo DMN để biểu diễn quy tắc và PROV để truy vết. Đây là chuẩn biểu diễn, không phải bằng chứng rằng lựa chọn đưa ra là đúng. [OMG DMN](https://www.omg.org/dmn/), [W3C PROV-O](https://www.w3.org/TR/prov-o/)

## 6. Chuyển báo cáo nghiên cứu thành cơ sở tri thức

```text
Báo cáo hiện có
  → xác định đoạn liên quan tới quyết định
  → tách khái niệm, mệnh đề, điều kiện và nhận định đánh giá
  → chuẩn hóa thuật ngữ theo từ điển chung
  → nối mệnh đề với nguồn và phạm vi áp dụng
  → kiểm tra, duyệt và lưu revision
  → chạy bộ ca kiểm chứng lựa chọn
```

Quy trình biên soạn đề xuất:

1. **Lập danh mục nguồn.** Chọn báo cáo chính cho từng catalog, revision của báo cáo và tập tài liệu gốc được tham chiếu. Không đếm hai báo cáo dẫn cùng một nguồn thành hai xác nhận độc lập.
2. **Chốt câu hỏi cần trả lời.** Từ ca sử dụng rút ra những kiến thức ảnh hưởng quyết định; không cần đưa toàn bộ nội dung kiến trúc vào bộ quy tắc.
3. **Biên soạn thử thủ công.** Chọn một nhóm tiêu chí phân biệt được ứng viên, áp dụng cùng mẫu cho cả sáu. Tránh chỉ xây sâu cho công nghệ đã ưa thích.
4. **Tách nội dung.** Định nghĩa đi vào từ điển; mệnh đề kỹ thuật vào claim; nhận xét như “dễ vận hành” phải có nghĩa quan sát được; khuyến nghị trong báo cáo là giả thuyết cần kiểm tra.
5. **Truy vết hai tầng.** Mỗi claim chỉ ra vị trí trong báo cáo và nguồn gốc bên dưới nếu có. Bài blog/báo cáo có thể giúp tìm thông tin; khẳng định quyết định cần mức bằng chứng đã chốt. Chưa tìm được nguồn thì giữ trạng thái chưa xác minh.
6. **Kiểm tra điều kiện.** Ghi rõ các khác biệt có thể đổi kết luận: edition, release, thao tác, format, API hoặc cơ chế quyền. Không điền thông tin không liên quan chỉ để làm manifest đầy đủ.
7. **Duyệt và đóng băng một revision.** Lưu người kiểm tra, vấn đề mở và lý do sửa. Khi nguồn thay đổi, xác định claim và kết quả lựa chọn nào cần xem lại.

Một phần báo cáo tổng quan hiện có chứa cả link tài liệu chính thức, bài phân tích bên ngoài và link nhánh phát triển. Đây là quan sát về danh mục nguồn, chưa phải thẩm định tính đúng của mọi mệnh đề. Ví dụ nên rà riêng các kịch bản tại [báo cáo tổng quan](<../../../technology-research/Công Nghệ Data Lakehouse Catalog.md>), tránh chuyển nguyên câu khuyến nghị sang quy tắc tuyệt đối.

Không cần LLM để hoàn thành quy trình này. Nghiên cứu SPIRES cho thấy một hướng trích xuất theo schema, nhưng không thay kiểm chứng mệnh đề; hướng đó chưa thuộc vai trò LLM người dùng đã chọn. [Caufield et al., 2024](https://doi.org/10.1093/bioinformatics/btae104)

## 7. Bộ câu hỏi kiểm tra năng lực cơ sở tri thức

Danh sách khởi đầu đề xuất; cần điều chỉnh theo các ca người dùng cung cấp:

| ID | Câu hỏi cơ sở tri thức phải hỗ trợ | Đầu ra mong đợi |
|---|---|---|
| CQ01 | Catalog nào đáp ứng tất cả điều kiện bắt buộc đã xác nhận? | Các catalog và căn cứ theo từng điều kiện |
| CQ02 | Vì sao catalog X bị loại? | Yêu cầu bị vi phạm, mệnh đề và bằng chứng |
| CQ03 | Điều gì chưa thể kết luận cho catalog X? | Thiếu tri thức, thiếu yêu cầu hoặc bằng chứng chưa đủ |
| CQ04 | Những khả năng cần thiết có áp dụng đồng thời trong cùng phạm vi không? | Phạm vi phù hợp hoặc điểm chưa xác minh |
| CQ05 | Nếu thay một ưu tiên thì khuyến nghị đổi thế nào? | Đánh đổi và điều kiện làm đổi kết quả |
| CQ06 | Hai nguồn khác nhau đang mâu thuẫn thật hay nói về ngữ cảnh khác? | Phân tách phạm vi hoặc vấn đề cần phân giải |
| CQ07 | Nếu không có catalog nào đáp ứng thì phải trả gì? | Lý do không có kết quả; yêu cầu cần làm rõ; không tự nới điều kiện |
| CQ08 | Một kết luận dựa trên những nguồn và quy tắc nào? | Chuỗi truy vết đủ để người khác kiểm tra |
| CQ09 | Sửa một mệnh đề ảnh hưởng tới những kết quả nào? | Danh sách phụ thuộc và ca cần chạy lại |

CQ02/CQ03/CQ07 đặc biệt quan trọng: một hệ thống chỉ trả tên catalog có thể hoạt động trên ví dụ thuận lợi nhưng chưa thể hiện khả năng xử lý thiếu tri thức hoặc yêu cầu không khả thi.

## 8. Thiết kế đánh giá cho đồ án

Phân biệt **dữ liệu đúng**, **bộ quy tắc chạy đúng**, **khuyến nghị hữu ích**. Sự đồng ý của người dùng về giao diện không chứng minh tính đúng của tri thức.

| Mức đánh giá | Cách kiểm tra đề xuất | Báo cáo |
|---|---|---|
| Chất lượng tri thức | Lấy mẫu claim theo catalog và nhóm tiêu chí; đối chiếu nguồn đúng phạm vi, có người duyệt độc lập nếu có thể | Tỷ lệ đúng trên mẫu, lỗi điều kiện, nguồn thiếu, mâu thuẫn; ghi cả mẫu số và cách chọn mẫu |
| Độ bao phủ theo mục đích | Dùng CQ và tập yêu cầu đã chốt làm mẫu số | Câu hỏi trả lời được, câu hỏi UNKNOWN và khoảng trống; không coi bao phủ schema là bao phủ mọi ca |
| Tính nhất quán | Kiểm tra kiểu dữ liệu, đơn vị, phạm vi, claim trái nhau, quy tắc trùng hoặc xung đột | Danh mục lỗi; validation schema không chứng minh mệnh đề đúng ngoài đời |
| Logic lựa chọn | Ca B=FAIL, B=UNKNOWN, yêu cầu mâu thuẫn, thay thứ tự trả lời, đổi ưu tiên, nguồn cũ | Kết quả và giải thích so với oracle của từng ca |
| Giá trị hỗ trợ quyết định | So prototype với quy trình đọc báo cáo/lập bảng thủ công trên ca chưa dùng để viết quy tắc | Công sức, lỗi bỏ sót điều kiện bắt buộc, độ truy vết, mức chấp nhận và ý kiến bất đồng |
| Khả năng bảo trì | Thử cập nhật một claim hoặc thêm một đặc tính | Công sửa, số quy tắc phải sửa và tác động tới các ca cũ |

Nếu dùng RDF, SHACL có thể kiểm tra hình dạng/điều kiện dữ liệu; mức sự thật và khuyến nghị vẫn cần đánh giá riêng. [W3C SHACL](https://www.w3.org/TR/shacl/)

Không đặt tùy ý “độ chính xác 90%” hoặc số ca đủ chứng minh tổng quát. Đầu tiên dùng ca phát triển để sửa phương pháp; sau đó đóng băng tri thức/quy tắc và đánh giá trên ca mới. Nếu có nhiều catalog hợp lý, oracle nên chứa tập kết quả chấp nhận được và các ràng buộc, thay vì một nhãn duy nhất. Nếu không có người duyệt độc lập, báo cáo rõ đây là tự kiểm tra và chưa chứng minh chất lượng quyết định thực tế.

Nếu chỉ đủ nguồn lực cho một prototype, ưu tiên A và một baseline thủ công. Không bắt buộc dựng thêm KG/RAG chỉ để đủ số giải pháp; chỉ làm đối chứng khi có câu hỏi nghiên cứu và nguồn lực tương ứng.

## 9. Thông tin còn cần để chốt thiết kế

Những thông tin đã có đủ để chọn hướng A làm giả thuyết chính. Thông tin có giá trị nhất tiếp theo:

1. **Hai hoặc ba ca lựa chọn mẫu:** nhu cầu, cái bắt buộc, ưu tiên và lý do có thể chấp nhận một catalog. Ca thật hay giả định phải được gắn nhãn.
2. **Người dùng mục tiêu:** người mới học, data engineer hay architect; họ hiểu và trả lời được những thuật ngữ nào trên form?
3. **Chính sách kết quả:** khi nhiều catalog cùng hợp lý hoặc không đủ bằng chứng, có chấp nhận shortlist/cần bổ sung thông tin không? Không tự áp quy tắc ép ra một tên.
4. **Bộ báo cáo nguồn chuẩn:** dùng file/revision nào, link nguồn gốc nào còn truy cập được; tiêu chí nào đã có bằng chứng thực nghiệm?
5. **Người duyệt và cách đánh giá:** có giảng viên/mentor/chuyên gia kiểm tra claim và ca lựa chọn không; họ chấp nhận loại bằng chứng nào?
6. **Thời hạn và phạm vi:** thời gian còn lại, có cần cập nhật thường xuyên hoặc mở rộng tập công nghệ sau prototype không?

Chưa cần hỏi người dùng muốn Neo4j, PostgreSQL, vector database hoặc thuật toán nào. Những lựa chọn kỹ thuật đó phải được dẫn xuất từ các câu hỏi và phép thử ở trên.

## 10. Đầu ra của giai đoạn nghiên cứu này

Đề xuất bộ sản phẩm nghiên cứu tiếp theo, **chưa được tạo thành dữ liệu hoàn chỉnh trong lượt này**:

1. Đặc tả phạm vi và CQ được chấp nhận.
2. Từ điển khái niệm và mô hình tri thức dùng chung cho sáu catalog.
3. Quy trình biên soạn từ báo cáo, chính sách bằng chứng và cập nhật.
4. Bộ claim mẫu có nguồn, giới hạn và trạng thái duyệt.
5. Mapping form–yêu cầu–đặc tính và quy tắc lựa chọn.
6. Prototype xử lý một lát cắt từ đầu vào tới tên catalog kèm lý do.
7. Bộ ca đánh giá và báo cáo kết quả so với baseline.

Khuyến nghị A hiện là quyết định thiết kế có điều kiện từ yêu cầu và tài liệu; chưa phải kết luận thực nghiệm rằng A tối ưu hoặc tốt hơn mọi cách biểu diễn khác.
