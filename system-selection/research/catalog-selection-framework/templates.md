# Biểu mẫu thực hiện framework

Phiên bản **v2 sau thẩm định, 13/10/2026**. **Chưa điền dữ liệu dự án hoặc kết quả thực nghiệm.** `TBD` = cần xác nhận, `null` = chưa có dữ liệu; không có nghĩa là 0/FAIL. ID trong mẫu là placeholder. Tham khảo [framework](README.md), [protocol](benchmark-protocol.md) và [báo cáo thẩm định](review-2026-10-13/review.md).

## 1. Requirement register

Một hàng cho một điều kiện có thể kiểm tra. Tách minimum bắt buộc khỏi ưu tiên nếu chúng thuộc cùng tiêu chí.

| Requirement ID | Nội dung và lý do | Người/nguồn xác nhận | C-ID | B/U/I | Scope và unit | Ngưỡng/quy tắc chấp nhận | Bằng chứng đủ | Scenario | Unknown/việc xác nhận |
|---|---|---|---|---|---|---|---|---|---|
| R-TBD | TBD | TBD | C-TBD | TBD | TBD | TBD | TBD | B-TBD hoặc tài liệu/ước tính | TBD |

Các ô bắt buộc bổ sung: revision/date; nguồn ngưỡng và lý do B không thể đánh đổi; trạng thái xác nhận/giả định; hậu quả vi phạm; đối tượng chịu tác động; ưu tiên và các đánh đổi được phép nếu U; người xác nhận N/A. Một outcome có `primary_C_ID` và các `related_C_IDs`; metric/unit/acceptance rule; dependency và task IDs để không đếm lặp. Không sao một evidence thành nhiều lợi ích độc lập.

### 1.1 Sàng lọc công nghệ và tính so sánh được

| Công nghệ | Cấu hình/đường tích hợp | Đủ điều kiện chức năng? | Có thể làm lab? | Được chọn vào mẫu? | Lý do/evidence/câu hỏi còn thiếu |
|---|---|---|---|---|---|
| Hive Metastore | TBD | UNKNOWN | TBD | Chưa chọn | TBD |
| AWS Glue Data Catalog | TBD | UNKNOWN | TBD | Chưa chọn | TBD |
| Apache Polaris | TBD | UNKNOWN | TBD | Chưa chọn | TBD |
| Project Nessie | TBD | UNKNOWN | TBD | Chưa chọn | TBD |
| Apache Gravitino | TBD | UNKNOWN | TBD | Chưa chọn | TBD |
| Unity Catalog OSS | TBD | UNKNOWN | TBD | Chưa chọn | TBD |

Cho mỗi cặp định so: ghi cùng/khác/chưa rõ về operation, transaction boundary, visibility, auth/storage enforcement, durability, service envelope, API và tổng phụ thuộc. Câu hỏi common-core và capability-specific phải có hàng riêng; thiếu thời gian triển khai không chuyển thành FAIL chức năng.

## 2. Manifest phương án và môi trường

Mẫu YAML là cấu trúc ghi chép, **không phải Docker Compose hoặc lệnh triển khai**. Tất cả version quan trọng phải là literal/digest đã xác minh trước khi chạy; không để `latest`.

```yaml
case_id: TBD
case_status: hypothetical_unconfirmed
method_revision: v2
decision_question: TBD
comparison_scope_and_functional_contract: TBD
source_commit_or_release_permalinks: []
requirements_revision: TBD
alternative_id: TBD
configuration_revision: TBD
catalog:
  product: TBD
  release: TBD
  image_digest: TBD
  documentation_release_url: TBD
  api_path_and_protocol: TBD
  enabled_endpoints: []
  server_effective_configuration_file: TBD
  server_retry_policy: TBD
  catalog_branch_if_any: TBD
  table_ref: TBD
  replicas: null
  cpu_limit: null
  memory_limit_gib: null
persistence:
  type: TBD
  release_and_driver: TBD
  schema_version: TBD
  durability_and_flush_settings: TBD
  cpu_memory_disk: TBD
  reset_restore_procedure: TBD
format:
  name_and_version: TBD
  schema_partition_codec: TBD
  metadata_fixture_hash: TBD
  namespace_table_snapshot_file_counts: TBD
  actual_metadata_bytes: null
storage:
  implementation_release_digest: TBD
  endpoint_region_topology: TBD
  prefix_pattern: TBD
  consistency_and_durability: TBD
  cpu_memory_disk_network: TBD
identity:
  authn_authz_policy: TBD
  idp_policy_services_and_resources: TBD
  token_ttl_refresh: TBD
  storage_credential_mode: TBD
  secret_reference_only: TBD
client:
  driver_build_and_dependency_lock: TBD
  iceberg_java_http_versions: TBD
  cpu_memory: TBD
  effective_config_including_server_overrides: TBD
  retry_timeout_deadline: TBD
  wire_attempt_verification: TBD
  deadline_start_and_remaining_budget_rule: TBD
  queue_capacity_admission_and_drain_policy: TBD
  cache_and_connections: TBD
engine_validation:
  spark_scala_iceberg_java_versions: TBD
  configuration: TBD
environment:
  host_os_cpu_ram_virtualization: TBD
  network_tls_proxy: TBD
  background_load_controls: TBD
  dependency_resource_budget: TBD
  time_sync_and_monotonic_clock: TBD
  telemetry_and_log_redaction: TBD
```

## 3. Evidence register

| Evidence ID | Mệnh đề cần xác minh | Alternative/config revision | R-ID/C-ID | Loại D/F/P/E | Nguồn/path, ngày, release | Phạm vi thực sự đọc/thử | Quan sát hoặc kết quả | Bất định/giới hạn | Reviewer |
|---|---|---|---|---|---|---|---|---|---|
| E-TBD | TBD | TBD | TBD | TBD | TBD | TBD | Chưa thu thập | TBD | TBD |

Ghi cả bằng chứng trái chiều. Link nguồn tài liệu cần section/page/commit, không chỉ trang chủ. Log thực nghiệm cần run ID và raw artifacts. Ước tính cần công thức, đơn giá, ngày và giả định. Không chứa secrets/token nguyên vẹn.

Ghi riêng source type; độ khớp với release/ca; test/harness validity; coverage; replication/reviewer status; uncertainty; conflicts. Không dùng thang xếp hạng E0–E3. `E-TBD` ở bảng là evidence ID, không phải mức confidence.

## 4. Criterion assessment

| Alternative/revision | R-ID/C-ID | B/U/I | PASS/FAIL/UNKNOWN/N/A | Giá trị/unit hoặc mô tả định tính | Evidence IDs | Source fit / validation / uncertainty | Giới hạn/việc tiếp theo |
|---|---|---|---|---|---|---|---|
| TBD | TBD | TBD | UNKNOWN | Chưa có dữ liệu | Chưa có | Chưa xác minh | TBD |

PASS phải ghi phạm vi; FAIL phải có điều kiện vi phạm; N/A cần người xác nhận. Dữ liệu chưa có không điền giá trị 0, điểm 1 hay chi phí 0.

## 5. Run plan và run record

Trước chạy điền: run ID; **pilot/main/amendment**; scenario; config/requirements revision; seed; fixture hash; offered rate/writers; bảng và append/bảng; schedule/operation limit; warm-up; measured window/drain; retry; oracle đã kiểm tra; counters; primary outcome; sample/inference/censoring plan; acceptance rule; resource limits; thứ tự run; fixed budget/stop/rerun rules. Sau chạy mới điền các trường sau:

```yaml
run_status: NOT_RUN
run_phase: TBD
analysis_plan_revision: TBD
harness_validation_artifact: null
started_at: null
ended_at: null
actual_config_hash: null
raw_operation_log_path: null
resource_metrics_path: null
oracle_report_path: null
actual_offered_rate: null
actual_achieved_goodput: null
goodput_denominator_definition: null
scheduled_operations: null
admission_failures: null
successful_logical_operations: null
attempts: null
expected_conflicts: null
timeouts: null
unresolved_operations: null
late_resolved_operations: null
latency_population_and_censoring: null
latency_summary_path: null
uncertainty_method_and_interval: null
oracle_outcome: null
protocol_deviations: []
interpretation_and_scope: null
```

Không gộp B1 API latency với B2 logical commit hoặc tổng thời gian query. Khi gộp nhiều run phải giữ dữ liệu từng run và cách xử lý correlation.

## 6. Cost worksheet

| Hạng mục | Quantity/unit | Đơn giá, currency, ngày, nguồn | Kỳ đánh giá | Giả định/khoảng | Đã có trong mục khác? |
|---|---|---|---|---|---|
| Catalog compute | TBD | TBD | TBD | TBD | TBD |
| DB và disk/backup | TBD | TBD | TBD | TBD | TBD |
| Storage API/bytes/network | TBD | TBD | TBD | TBD | TBD |
| IdP/policy/proxy/support | TBD | TBD | TBD | TBD | TBD |
| Triển khai và đào tạo ban đầu | TBD giờ | TBD | Một lần | TBD | TBD |
| Vận hành định kỳ | TBD giờ | TBD | TBD | TBD | TBD |
| Migration/exit | TBD giờ/bytes | TBD | Theo phạm vi | TBD | TBD |

Nếu chưa có đơn giá, trình bày quantities/giờ công; không chuyển thành lợi ích tiền tệ tự đặt. So baseline ở cùng scope, kỳ và mức dịch vụ. Ghi chi phí chìm, phí cố định và chi phí tăng thêm riêng nếu cần quyết định thay thế. Không tính cùng giờ công vừa vào deployment vừa vào migration.

Mỗi hàng có task ID, owner/operator/kinh nghiệm và source; phân biệt machine time, active human time, learning và recurring operations. Ghi loại kết luận: lab resource ledger / dự toán kịch bản / lợi ích quan sát thực tế. Ghi service envelope, baseline, kỳ H và adoption/workload nếu ngoại suy; các ô chưa biết để TBD. Không đổi giảm giờ công lab thành lợi nhuận đã đạt.

## 7. Decision record

```text
Case / requirements revision:
Người xác nhận và ngày:
Phạm vi ứng dụng, workload, hạ tầng:
Giả định chưa xác nhận:

Trước thực nghiệm:
- Shortlist tài liệu:
- Khuyến nghị tạm thời (nếu có):
- Những câu hỏi benchmark có thể làm đổi quyết định:

Sau đánh giá (chưa điền ở bước thiết kế):
- Đủ điều kiện trong phạm vi đã kiểm tra:
- Bị loại và R-ID/E-ID chứng minh:
- Chờ xác minh và bằng chứng còn thiếu:
- Khuyến nghị / hoặc lý do giữ shortlist:
- Quy tắc ưu tiên đã được xác nhận:
- Đánh đổi chấp nhận, lợi ích từ bỏ, phụ thuộc bổ sung:
- Kết quả benchmark đã làm đổi nhận định nào:
- Độ vững bằng chứng theo mệnh đề:
- Độ bền khuyến nghị trên các kịch bản đã xét:
- Nhãn: chưa kết luận / có điều kiện / có bằng chứng trực tiếp và ổn định trong các kịch bản đã xét:
- Điều kiện làm đổi khuyến nghị:
- Phạm vi không được ngoại suy:
- Việc tiếp theo, người phụ trách:
- Reviewer và ý kiến khác biệt:
```

## 8. Sensitivity register

| Biến/giả định | Miền thay đổi có căn cứ | Nguồn miền | Ràng buộc/đánh đổi ảnh hưởng | Khuyến nghị có đổi không? | Hành động |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | Chưa đánh giá | TBD |

Ví dụ loại biến cần xét: tải/metadata size, ngân sách, công vận hành, yêu cầu engine thứ hai, cho phép experimental, migration bắt buộc. Đây là ví dụ biến, không phải dữ liệu dự án. Không gán xác suất cho kịch bản khi chưa có căn cứ.

## 9. Kiểm chứng phương pháp (chưa thực hiện)

| Ca/revision | Evidence pack chung | Reviewer và kinh nghiệm | Thời gian dùng framework | Kết luận không truy được nguồn | Bất đồng B/U hoặc phạm vi | Có tái dựng được shortlist? | Giới hạn |
|---|---|---|---|---|---|---|---|
| TBD | TBD | TBD | Chưa đo | Chưa đánh giá | Chưa đánh giá | Chưa đánh giá | TBD |

Ghi kết quả các tình huống kiểm tra logic: B fail, B unknown, evidence trùng, source/version đổi. Nếu có baseline bảng so sánh thường, dùng cùng dữ liệu và ghi thứ tự/learning effect. Không coi reviewer đồng ý với lựa chọn là chứng minh lựa chọn tối ưu.
