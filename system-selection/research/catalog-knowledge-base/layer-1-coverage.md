# Độ bao phủ thu thập dữ liệu lớp 1

Revision: `layer1-v3-data-2026-10-17-r1`. Ngày: **17/10/2026**.

Bảng kiểm kê **37 thuộc tính × 7 scope**. `K` = số claim có kết luận dựa trên nguồn (gồm full/none và giá trị đã biết); `U` = claim ghi rõ unknown/null; `—` = chưa thu claim. Một ô có K chỉ chứng minh các qualifier được ghi, không phải toàn bộ thuộc tính hoặc sản phẩm. Số K không phải điểm phù hợp.

| Property | Polaris | Gravitino | Nessie | UC OSS | UC Databricks AWS | Glue | HMS |
|---|---:|---:|---:|---:|---:|---:|---:|
| `catalog.format_operation` | 4K | 2K | 1K | 3K | 4K | 3K | 2K |
| `catalog.object_operation` | 1K | 1K | — | — | 5K | — | — |
| `metadata.responsibility` | 1K | 1K | 1K | — | 1K | 1K | 1K |
| `integration.engine_operation` | 2K | 3K | 2K | 4K | 1K | 3K | 3K |
| `integration.api_operation` | — | — | 1K | 1K | — | — | — |
| `integration.streaming_write` | — | — | — | — | — | — | — |
| `authentication.method` | 2K | 3K | 1K | 2K | 2K | 1K | — |
| `authentication.identity_provider` | — | — | 1K | 1K | — | — | — |
| `authentication.session_control` | 1K | — | — | — | — | — | — |
| `authorization.policy_model` | 1K | 2K | 1K | 1K | 2K | 1K | 1K |
| `security.authorization` | 1K | 2K/1U | 2K | 1K | 2K | 2K | 2K |
| `authorization.external_policy` | — | — | — | — | — | 1K | — |
| `storage.backend` | 3K | 4K | 2K | 3K | — | 1K | 1K |
| `storage.access_method` | 1K | 1K | 1K | 1K | — | — | 1K |
| `storage.credential_vending` | 3K | 2K | — | 1U | 1K/1U | 1K | — |
| `storage.credential_lifecycle` | 1K | 1K | — | — | — | — | — |
| `commit.guarantee` | — | — | 1K | — | — | 1K | — |
| `commit.concurrent_write` | — | — | — | — | — | 1K | — |
| `transaction.multi_table_atomic` | — | 1K | 1K/1U | — | — | — | — |
| `workflow.branching` | — | — | 1K | — | — | — | — |
| `versioning.operation` | — | 1K | 2K | — | — | — | — |
| `metadata.federation_operation` | 1K | 1K | — | — | 4K | — | — |
| `migration.asset_preservation` | — | — | 1K | — | — | — | — |
| `deployment.environment` | 1K | 1K | 1K | 1K | 1K | 1K | 1K |
| `deployment.dependencies` | 1K | — | — | — | 1K | — | 1K |
| `persistence.backend` | 1K | 2K | 1K | 2K | — | — | 3K |
| `operations.capability` | 3K | 1K | 2K | 1K | — | 1K | 1K |
| `governance.audit` | — | — | — | — | 1K | 1K | — |
| `governance.lineage` | — | 1K | — | — | 1K | — | — |
| `security.data_protection` | — | — | — | — | — | 1K | — |
| `limits.quota` | 1U | 1U | 1U | 1U | 2K | 2K | 1U |
| `performance.observation` | 1U | 1U | 1U | 1U | 1U | 1U | 1U |
| `operations.effort_observation` | 1U | 1U | 1U | 1U | 1U | 1U | 1U |
| `cost.price_component` | 1U | 1U | 1U | 1U | 1U | 1U | 1U |
| `project.license` | 1K | — | 1K | 1K | — | — | 1K |
| `project.support_policy` | — | — | — | — | — | — | — |
| `project.maintenance_context` | — | — | — | — | — | — | — |

Dữ liệu: [layer-1-data.json](layer-1-data.json). Chi tiết ID claim và khoảng trống: [layer-1-coverage.json](layer-1-coverage.json). Điều kiện và mâu thuẫn nguồn: [ghi chú nghiên cứu](layer-1-research-notes.md).
