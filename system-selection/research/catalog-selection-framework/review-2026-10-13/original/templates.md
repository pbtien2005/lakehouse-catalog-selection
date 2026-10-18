# Biểu mẫu thực hiện framework

Ngày: 13/10/2026. **Biểu mẫu chưa điền dữ liệu dự án hoặc kết quả thực nghiệm.** `TBD` = cần xác nhận, `null` = chưa có dữ liệu; không có nghĩa là 0/FAIL. ID trong mẫu là placeholder. Tham khảo [framework](README.md) và [protocol](benchmark-protocol.md).

## 1. Requirement register

Một hàng cho một điều kiện có thể kiểm tra. Tách minimum bắt buộc khỏi ưu tiên nếu chúng thuộc cùng tiêu chí.

| Requirement ID | Nội dung và lý do | Người/nguồn xác nhận | C-ID | B/U/I | Scope và unit | Ngưỡng/quy tắc chấp nhận | Bằng chứng đủ | Scenario | Unknown/việc xác nhận |
|---|---|---|---|---|---|---|---|---|---|
| R-TBD | TBD | TBD | C-TBD | TBD | TBD | TBD | TBD | B-TBD hoặc tài liệu/ước tính | TBD |

Các ô bổ sung: revision/date; đối tượng chịu tác động; mức ưu tiên nếu U; tương tác/trùng lợi ích với yêu cầu khác; người xác nhận N/A; thời điểm cần có câu trả lời.

## 2. Manifest phương án và môi trường

Mẫu YAML là cấu trúc ghi chép, **không phải Docker Compose hoặc lệnh triển khai**. Tất cả version quan trọng phải là literal/digest đã xác minh trước khi chạy; không để `latest`.

```yaml
case_id: TBD
case_status: hypothetical_unconfirmed
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

## 4. Criterion assessment

| Alternative/revision | R-ID/C-ID | B/U/I | PASS/FAIL/UNKNOWN/N/A | Giá trị/unit hoặc mô tả định tính | Evidence IDs | Độ vững bằng chứng | Giới hạn/việc tiếp theo |
|---|---|---|---|---|---|---|---|
| TBD | TBD | TBD | UNKNOWN | Chưa có dữ liệu | Chưa có | E0 | TBD |

PASS phải ghi phạm vi; FAIL phải có điều kiện vi phạm; N/A cần người xác nhận. Dữ liệu chưa có không điền giá trị 0, điểm 1 hay chi phí 0.

## 5. Run plan và run record

Trước chạy điền: run ID; scenario; config/requirements revision; seed; fixture hash; offered rate/writers; schedule/operation limit; warm-up; measured window; retry; oracle; counters; acceptance rule; resource limits; thứ tự run; stop/rerun rules. Sau chạy mới điền các trường sau:

```yaml
run_status: NOT_RUN
started_at: null
ended_at: null
actual_config_hash: null
raw_operation_log_path: null
resource_metrics_path: null
oracle_report_path: null
actual_offered_rate: null
actual_achieved_goodput: null
successful_logical_operations: null
attempts: null
expected_conflicts: null
timeouts: null
unresolved_operations: null
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
- Nhãn: chưa kết luận / có điều kiện / vững trong phạm vi đã thử:
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
