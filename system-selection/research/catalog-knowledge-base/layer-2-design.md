# Lớp 2 v2 — hợp đồng và runtime

**Trạng thái hiện hành:** đã có [bảng quy đổi](layer-2-kb-values.json) và `run_case` nối Lớp 2 → validator → bốn bước Lớp 3 → UI. Xem [hướng dẫn MVP](../catalog-reasoner-mvp/README.md) và [báo cáo cuối](../catalog-reasoner-mvp/outputs/mvp/final-report.md). Candidate bindings vẫn chỉ là trace. Phần dưới ghi lại mốc Nhóm 1; các câu “chưa” hoặc “nhóm sau” trong phần này là trạng thái lịch sử.

Ngày: **17/10/2026**. Chuẩn duy nhất: [form v2](input-v2.md), [registry ID](form-v2-registry.json). Người dùng đã chọn **cả bảy scope thật** trong KB; giới hạn ba ứng viên trước đây không còn áp dụng.

## Phạm vi hiện tại

Đã có runtime Python thuần `normalize_form(payload, assets)` tại [layer2.py](../catalog-reasoner-mvp/catalog_reasoner/layer2.py), loader/CLI tại [layer2_io.py](../catalog-reasoner-mvp/catalog_reasoner/layer2_io.py). Runtime tạo requirements, objectives, unresolved, input_issues, reminders, trace, assumptions và danh sách bảy candidate. Không tra mức claim, không tính điểm và không chạy Lớp 3 trong Nhóm 1.

[Mapping](layer-2-mapping.json) đọc 48 đáp án từ registry bằng answers_ref; không giữ một bản sao danh sách ID riêng. UI đọc chính registry này qua route cố định `/form-v2-registry.json`. I06 giữ ba đáp án trong registry nhưng bất hoạt, không gửi từ UI.

## Diễn giải đã được xác nhận

- I01–I03 cụ thể tạo HARD/full khi `default_environment_facts_as_hard=true` trong [config Lớp 2](layer-2-runtime-config.json). Reminder hiển thị đúng câu “đã coi lựa chọn này là bắt buộc”. Đảo cờ thành false thì các lựa chọn này chỉ là context, không biến thành SOFT.
- Đa cloud, Hỗn hợp, Chưa chọn và engine Khác giữ unresolved; không tạo HARD trực tiếp từ đáp án đó. Nhóm engine cũ được báo lỗi cần chọn lại và giữ unresolved, không tự tách hoặc áp HARD.
- I04 tạo yêu cầu quantity với khoảng lấy từ config, `min_level_if_applicable=null`. Chưa thực hiện so quota; phần đó thuộc Nhóm 3.
- I05 từ hai engine tạo yêu cầu concurrent append ở cấp catalog theo profile; không suy thành atomic nhiều bảng hoặc đã xác minh các engine ghi cụ thể.
- I07 có table/column/row/cả hai/none/unclear. I08 Có tạo HARD với storage chưa rõ; Không khác Chưa biết. Không có trường storage mới trong payload.
- I09 là context tùy chọn; không tự lọc hoặc đổi weight.
- I10 chỉ có mandatory và nice_to_have. Mandatory tạo HARD; nice_to_have lấy raw weight thấp từ file config suy luận hiện có, theo `nice_to_have_weight_rank=low`, và luôn ghi `weight_defaulted=true`. Không thêm important và không chuẩn hóa hoặc tính điểm trong Lớp 2.

Các trọng số hiện có tại [config suy luận](../catalog-reasoner-mvp/config.json) giữ nguyên. Numeric boundaries của số bảng nằm trong config Lớp 2. Giá trị mặc định đã dùng và nguồn đều có trong assumptions hoặc profile_assumptions đầu ra.

## Payload

```json
{"form_revision":"input-v2","answers":{"I01":"aws","I02":["spark","trino"],"I03":"iceberg","I04":"100_to_999","I05":"two_to_three","I07":"table","I08":"unknown","I09":["none"],"I10":{"none":false,"selected":[{"feature":"branching","rank":"nice_to_have"}]}}}
```

Không gửi trường ngoài registry hoặc nhãn hiển thị thay ID. Runtime không sửa raw answers. None cùng lựa chọn cụ thể, thiếu/sai rank, sai cardinality, ID cũ hoặc ID lạ trả lỗi có đường dẫn trường; readiness là needs_input_correction. Các câu chưa trả lời được giữ unresolved, không tự điền default thuận lợi.

## Lệch phạm vi đã xử lý

- Gỡ operations, portability, storage, priorities và tên hồ sơ khỏi payload form chính thức; UI form không còn hỏi các mục ngoài v2.
- Gỡ các bậc important/off/unknown của bộ ưu tiên UI cũ. Hai rank còn lại đọc từ registry; Chưa biết ở I08 và Chưa rõ ở I07 vẫn là đáp án riêng.
- Tách Trino/Presto và StarRocks/Doris; thêm Khác và Hỗn hợp; sửa khoảng số bảng, mức phân quyền và bổ sung I09.
- Gỡ evaluator và sáu capability fixture JavaScript. UI chỉ chuẩn bị payload hoặc trình bày kết quả backend được cấp; chưa có backend thì hiển thị trạng thái chờ, không tạo điểm hoặc nhóm thay thế.
- Giữ stylesheet và vỏ trang hiện tại. Đây là thay đổi hợp đồng/điều khiển theo registry, chưa phải vòng chỉnh thiết kế thị giác.

## Giới hạn có chủ đích và các nhóm sau

`candidate_bindings` chỉ là trace. Không thực thi joint_path_resolution hoặc tìm tổ hợp API/path trong MVP theo quyết định mới. Các tên qualifier và điều kiện gốc vẫn được giữ; không tự bỏ điều kiện để tìm claim.

Không quy đổi aws/read/append/multi_engine hoặc các chuỗi khác sang giá trị KB ở Nhóm 1. Bảng quy đổi có nguồn lý do và khoảng trống phủ KB thuộc Nhóm 2; chưa tự coi các chuỗi đồng nghĩa. Validator Lớp 3 và quota thuộc Nhóm 3. Tính điểm/kịch bản thuộc Nhóm 4; run_case chính thức và kiểm tra đổi đáp án xuyên suốt thuộc Nhóm 5.

Lớp 1, config trọng số suy luận và toàn bộ property-plan được giữ nguyên; bao gồm 25 property không có câu form tham chiếu trực tiếp. Property-plan chỉ là kế hoạch thu thập, không là nguồn runtime để xác định trọng số.

## Kiểm chứng

[Script kiểm tra](layer-2-checks.py) thực thi từng nhánh của 48 đáp án qua normalizer, đối chiếu property/anchor/registry và ghi hash hiện tại vào [báo cáo](layer-2-validation.json). [Các hồ sơ kiểm tra](layer-2-examples.json) được đặt tên SYNTHETIC: đây là profile tổng hợp trên metadata ứng viên thật, không phải đánh giá sản phẩm.

Kiểm thử trình duyệt lưu payload thực tại [group1-payload.json](../../sites/catalog-review/artifacts/group1-payload.json); CLI Lớp 2 chuẩn hóa chính payload này ra [group1-ui-normalized.json](../catalog-reasoner-mvp/outputs/group1-ui-normalized.json). Luồng được chạy ở đây là UI → Lớp 2, không phải UI → Lớp 3.
