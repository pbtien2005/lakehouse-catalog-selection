# Review Nhóm 1 — Lớp 2 khớp form v2

Ngày kiểm chứng: 17/10/2026. **Đã hoàn thành Nhóm 1, dùng cả bảy scope thật.** Dừng tại mốc review người dùng yêu cầu; chưa thực hiện Nhóm 2–5.

## Phạm vi đã thực hiện

- Registry máy đọc được là nguồn ID chung cho UI và mapping: 10 câu, 48 đáp án; I06 vẫn bất hoạt nên UI có 9 câu.
- Mapping v2 đủ 48 nhánh. Bốn ID cũ không còn là đáp án hợp lệ; nếu gửi lại thì báo đúng trường, giữ unresolved và không tự tách nhóm.
- Runtime thuần `normalize_form(payload, assets)` tạo đầu ra theo output_contract. Loader kiểm tra ID câu, ID đáp án và tham chiếu JSON Pointer từ mapping vào registry.
- I01–I03 cụ thể mặc định HARD theo cờ config, kèm reminder “đã coi lựa chọn này là bắt buộc”. Đa cloud, Hỗn hợp, Chưa chọn và Khác không tự thành HARD.
- I10 chỉ có mandatory/nice_to_have; nice_to_have dùng raw weight thấp từ config suy luận hiện có và ghi `weight_defaulted=true`.
- Candidate bindings chỉ ghi trace; chưa tìm path, tổ hợp API hoặc diễn giải alias giữa miền Lớp 2 và KB.
- UI chuẩn bị payload và chỉ trình bày quyết định do backend cung cấp. Chưa nối backend thì hiện “Chưa có kết quả từ backend”; không dựng kết quả thay thế.

## Bảy scope được chọn

| Catalog | Scope ID trong KB |
|---|---|
| Apache Polaris OSS | `polaris_oss_1_7_0` |
| Apache Gravitino OSS | `gravitino_oss_1_1_0` |
| Project Nessie OSS | `nessie_oss_2026_10_17` |
| Unity Catalog OSS | `unity_oss_2026_10_17` |
| Unity Catalog Databricks AWS | `unity_databricks_aws_2026_10_17` |
| AWS Glue Data Catalog | `glue_aws_2026_10_17` |
| Hive Metastore OSS | `hms_oss_2026_10_17` |

Đây là metadata ứng viên thật lấy nguyên từ KB. Các hồ sơ dùng kiểm thử đều là **dữ liệu tổng hợp**, không phải đánh giá năng lực các sản phẩm.

## Kiểm thử đã chạy thật

| Kiểm tra | Kết quả | Bằng chứng |
|---|---|---|
| Python | 124 qua, không lỗi/skip; gồm 87 test Lớp 2 và 37 test Lớp 3 cũ | [JUnit](group1-tests.xml), [coverage](group1-coverage.json) |
| JavaScript hợp đồng form | 23 qua, không lỗi/skip; core.js 100% dòng, 97,22% nhánh | [log](../../../sites/catalog-review/artifacts/group1-js-tests.log), [JUnit](../../../sites/catalog-review/artifacts/group1-js-tests.xml) |
| Lớp 2: registry/mapping/property/anchor/hash | 74 qua, gồm thực thi 48 đáp án | [báo cáo có SHA256](../../catalog-knowledge-base/layer-2-validation.json) |
| Trình duyệt: hợp đồng form | 4 nhóm kiểm tra qua, không page error | [browser smoke](../../../sites/catalog-review/artifacts/group1-browser-check.json) |
| Payload thật từ browser → CLI Lớp 2 | `ready_for_assessment`, 7 candidate, `layer3_executed=false` | [payload](../../../sites/catalog-review/artifacts/group1-payload.json), [đầu ra đầy đủ](group1-ui-normalized.json) |

Browser smoke đã kiểm tra ID đáp án, giữ nguyên Chưa biết, lỗi chọn Không cùng mục khác, lỗi thiếu rank, lưu/khôi phục payload và không tạo fixture result. Chưa phải vòng QA thị giác, bàn phím hoặc giao diện kết quả suy luận cuối cùng.

Đã tái hiện test thất bại trước khi sửa tham chiếu registry và loader, sau đó chạy lại thành công. Những phép đo kiểm thử không phải tham số mô hình.

## Lệch phạm vi đã xử lý

- Gỡ `operations`, `portability`, `storage`, `priorities` và tên hồ sơ khỏi payload chính thức.
- Gỡ năm bậc ưu tiên cũ; chỉ giữ hai rank theo registry, không thêm important.
- Gỡ evaluator quyết định độc lập và sáu fixture năng lực ở JavaScript.
- Gỡ mô tả cũ hứa tự tìm path và cho phép override bằng case context ngoài form trong các tài liệu đang dùng.

Giữ nguyên KB Lớp 1, từ điển 37 property, property-plan gồm 25 property không tham chiếu trực tiếp, config suy luận/trọng số và stylesheet. Script kiểm tra đối chiếu SHA256 với bản trước sửa. Config Lớp 2 riêng chỉ chứa chính sách đã xác nhận, danh sách bảy scope, khoảng số bảng và nguồn config suy luận.

## Tham số và giả định đã công khai

- `default_environment_facts_as_hard=true`, ngưỡng support HARD là full.
- Nice-to-have lấy `rank_to_weight.low=1` từ config suy luận hiện có; chỉ đưa vào assumptions khi dùng SOFT. Không chuẩn hóa hoặc chấm điểm tại Lớp 2.
- Khoảng số bảng: [0,99], [100,999], [1000,10000], [10001,null], lấy từ config Lớp 2; không tự lấy trung điểm.
- Profile dùng read/load metadata, số bảng trong một catalog, concurrent append/multi_engine, branching cấp catalog, atomic publication tại catalog_metadata_commit, federation read_metadata. Không suy storage từ cloud.
- Các giá trị mặc định đã dùng xuất hiện trong `assumptions` hoặc `profile_assumptions`; nguồn và revision có trong output. Tham số tính điểm/kịch bản của Lớp 3 chưa được dùng.

## Điểm dừng và việc cần quyết

| Nhóm | Trạng thái | Việc tiếp theo |
|---|---|---|
| 1 — Lớp 2/form v2 | Qua trong phạm vi trên | Người dùng review đầu ra và xác nhận sang Nhóm 2 |
| 2 — Miền giá trị Lớp 2 → KB | Chưa làm | Bảng ánh xạ tường minh và khoảng trống phủ KB; không tự đoán đồng nghĩa |
| 3 — Validator Lớp 3 | Chưa làm | Readiness, từ điển, rubric và phép so quota |
| 4 — Suy luận đầy đủ | Chưa làm | Điểm khoảng, kịch bản, regret, ảnh hưởng unknown và trace |
| 5 — Nối chính thức | Chưa làm | run_case, perturbation qua đường chính thức và ba hồ sơ đầy đủ |

`ready_for_assessment` ở đây chỉ có nghĩa payload không có lỗi nhập liệu; requirements vẫn có thể thiếu qualifier hoặc có unresolved. Không có kết luận ứng viên đủ điều kiện hay xếp hạng sản phẩm trong Nhóm 1.

## Đề xuất sau MVP

Chưa thêm đề xuất tính năng. Các việc Nhóm 2–5 ở trên thuộc phạm vi người dùng đã yêu cầu, không phải mở rộng MVP.
