# Lớp 1 v3 — cơ sở tri thức kỹ thuật về lakehouse catalog

Ngày: **17/10/2026**. Bản hiện hành, thay v2 đã lưu tại [archive v2](archive/layer-1-v2/README.md).

**Mục tiêu:** xác định nội dung cần thu thập và cách ghi nhất quán cho hệ thống chọn catalog. Bộ thiết kế/từ điển khác bộ dữ liệu đã điền. Đã có [lát cắt dữ liệu từ nguồn chính thức](layer-1-research-notes.md) cho 7 công nghệ theo danh sách người dùng bổ sung ngày 17/10/2026; chưa bao phủ mọi tổ hợp hoặc kiểm chứng runtime. Không đổi [input đã chốt](input-v1.md), không gán điểm số mặc định.

## 1. Lớp 1 lưu những gì?

Lớp 1 lưu **catalog hỗ trợ table format nào, kết nối engine nào, xác thực và phân quyền ra sao, truy cập storage thế nào, commit/transaction có bảo đảm gì, có những khả năng quản trị/vận hành nào**. Các quan sát quy mô, giá và thông tin dự án được giữ đúng bản chất dữ liệu.

Đơn vị ghi là: **một thông tin kỹ thuật + catalog/edition/release + điều kiện áp dụng + nguồn**. Một thuộc tính có thể có nhiều claim theo engine, format, storage hoặc thao tác. Không phải một catalog có đúng một ô tổng quát cho mỗi nhóm.

Phạm vi nghiên cứu theo yêu cầu cập nhật: Hive Metastore, AWS Glue Data Catalog, Apache Polaris, Project Nessie, Apache Gravitino, Unity Catalog OSS và Unity Catalog trên Databricks. Managed dựa trên một dự án OSS không tự được gộp vào dự án đó; scope Databricks hiện thu tài liệu AWS. Chưa chốt tập con ba ứng viên.

Bản này giữ cấu trúc nhẹ của v2 nhưng sửa hai thiếu sót: **bổ sung authentication và các nhóm miền còn thiếu**, đồng thời **không ép mô tả, license và số đo thành nhãn none/partial/full**.

## 2. Danh mục nội dung: 11 nhóm, 37 thuộc tính

Các thuộc tính dưới đây là từ điển miền, không phải 37 tiêu chí độc lập để cộng điểm và không bắt buộc điền mọi tổ hợp cho mọi catalog. Những định nghĩa và giới hạn đọc bằng máy nằm tại [từ điển properties](layer-1-properties.json).

### 1. Table format và mô hình metadata

Phân biệt table format (Iceberg/Delta/Hudi) với file format (Parquet/ORC/Avro). Mức hỗ trợ phải nêu thao tác: register/load/create/alter/drop hoặc tính năng liên quan; một nhãn format không thay ma trận engine đọc/ghi. Metadata pointer, snapshot và file metadata có thể thuộc các thành phần khác nhau.

| Property ID | Thông tin cần thu thập | Điều kiện phải chỉ rõ | Kiểu |
|---|---|---|---|
| `catalog.format_operation` | Khả năng thực hiện một thao tác catalog/metadata đối với table format được chỉ rõ. | `format`, `operation`, `api` | Trạng thái hỗ trợ |
| `catalog.object_operation` | Khả năng biểu diễn và quản lý namespace, table, view hoặc đối tượng được chỉ rõ. | `object_type`, `operation`, `api` | Trạng thái hỗ trợ |
| `metadata.responsibility` | Thành phần có thẩm quyền lưu hoặc cập nhật một loại trạng thái metadata. | `metadata_kind` | Mô tả kỹ thuật |

### 2. Engine, API và streaming

Tách Spark/Trino/Presto/Flink/Snowflake/Databricks/Dremio/StarRocks/Doris/DuckDB thành các giá trị riêng trong tri thức. Ghi path API/connector và thao tác; phiên bản chỉ ghi như điều kiện khi làm đổi kết luận. Streaming là đường ghi của engine/connector, không phải một cờ xử lý luồng của catalog.

| Property ID | Thông tin cần thu thập | Điều kiện phải chỉ rõ | Kiểu |
|---|---|---|---|
| `integration.engine_operation` | Đường tích hợp cho một engine thực hiện một thao tác trên một format trong scope đang xét. | `engine`, `format`, `operation`, `api` | Trạng thái hỗ trợ |
| `integration.api_operation` | Khả năng cung cấp một thao tác qua giao thức/API được xác định. | `api`, `operation` | Trạng thái hỗ trợ |
| `integration.streaming_write` | Đường ghi streaming hoặc micro-batch cụ thể qua engine và connector tương ứng. | `engine`, `format`, `mode`, `api` | Trạng thái hỗ trợ |

### 3. Authentication — xác thực

Đây là nhóm bắt buộc có trong từ điển dù form chưa hỏi trực tiếp. Thu cách client chứng minh danh tính, IdP được tích hợp và vòng đời token. OAuth2 grant, OIDC, JWT và validation token phải ghi đúng vai trò; không coi chúng đồng nghĩa hoặc suy hỗ trợ mọi IdP từ một hướng dẫn minh họa.

| Property ID | Thông tin cần thu thập | Điều kiện phải chỉ rõ | Kiểu |
|---|---|---|---|
| `authentication.method` | Cơ chế xác thực principal/client tới dịch vụ catalog qua API xác định. | `method`, `api` | Trạng thái hỗ trợ |
| `authentication.identity_provider` | Khả năng dùng một IdP hoặc loại IdP xác định trong đường xác thực. | `identity_provider`, `protocol`, `api` | Trạng thái hỗ trợ |
| `authentication.session_control` | Khả năng thực hiện một tác vụ như cấp, kiểm tra hết hạn, làm mới hoặc thu hồi token/phiên. | `action`, `api` | Trạng thái hỗ trợ |

### 4. Authorization — phân quyền

Phân biệt mô hình chính sách với nơi thực thi. Ghi rõ catalog/namespace/table/row/column, hành động, engine/API/storage path và các thành phần ngoài nếu cần. Catalog có RBAC hoặc policy metadata chưa chứng minh lọc hàng/cột qua mọi engine.

| Property ID | Thông tin cần thu thập | Điều kiện phải chỉ rõ | Kiểu |
|---|---|---|---|
| `authorization.policy_model` | Khả năng áp dụng mô hình quyền được chỉ rõ như role-based hoặc attribute-based tại catalog. | `model`, `api` | Trạng thái hỗ trợ |
| `security.authorization` | Thực thi allow/deny cho một hành động ở cấp tài nguyên và đường truy cập cụ thể. | `granularity`, `action`, `access_path` | Trạng thái hỗ trợ |
| `authorization.external_policy` | Đường tích hợp một hệ thống quyết định/thực thi chính sách bên ngoài. | `policy_engine`, `access_path` | Trạng thái hỗ trợ |

### 5. Storage và cấp quyền truy cập dữ liệu

Tách storage implementation khỏi nơi chạy engine. AWS S3 khác MinIO/Ceph/Ozone dù cùng họ API S3; khả năng sử dụng storage, credential vending và request signing là các thông tin khác nhau. Không lưu credential thật hoặc tên khóa cấu hình client vào KB quyết định.

| Property ID | Thông tin cần thu thập | Điều kiện phải chỉ rõ | Kiểu |
|---|---|---|---|
| `storage.backend` | Khả năng sử dụng backend lưu dữ liệu được xác định qua đường catalog đang xét. | `storage`, `api` | Trạng thái hỗ trợ |
| `storage.access_method` | Các cơ chế truy cập storage được mô tả, ví dụ credential vending, request signing hoặc danh tính được cấp riêng. | `storage`, `api` | Tập giá trị |
| `storage.credential_vending` | Catalog trả credential storage tạm thời, giới hạn theo dữ liệu/quyền được phép trong phạm vi đã xác định. | `storage`, `api` | Trạng thái hỗ trợ |
| `storage.credential_lifecycle` | Khả năng cấp lại, làm mới, hết hạn hoặc thu hồi quyền storage theo tác vụ được xác định. | `storage`, `action`, `api` | Trạng thái hỗ trợ |

### 6. Commit, concurrency và transaction

Ghi atomicity, optimistic/pessimistic concurrency, conflict detection, retry, commit-status-unknown và read-after-write theo operation/boundary thực sự có bằng chứng. Các cơ chế là mô tả kỹ thuật, không mặc định optimistic tốt hơn pessimistic. Transaction nhiều bảng phải bao gồm đường client và lỗi trong phạm vi bảo đảm.

| Property ID | Thông tin cần thu thập | Điều kiện phải chỉ rõ | Kiểu |
|---|---|---|---|
| `commit.guarantee` | Hợp đồng atomicity, trạng thái commit, visibility, xử lý conflict/retry của một thao tác và boundary. | `operation`, `boundary`, `api` | Mô tả kỹ thuật |
| `commit.concurrent_write` | Hỗ trợ concurrent commit theo loại thao tác và mô hình writer đang xét. | `operation`, `writer_topology`, `api` | Trạng thái hỗ trợ |
| `transaction.multi_table_atomic` | Bảo đảm all-or-nothing của các cập nhật nhiều bảng qua đường client/API và failure boundary được nêu. | `client_path`, `failure_boundary`, `api` | Trạng thái hỗ trợ |

### 7. Branching và versioning

Phân biệt nhánh của một bảng, một tập bảng và cả catalog; branch, tag, snapshot và lịch sử entity không thay thế nhau. Workflow nhánh có rubric riêng. Time travel/rollback phải chỉ rõ thao tác, đối tượng và điều kiện; công bố một branch không tự chứng minh mọi semantics all-or-nothing.

| Property ID | Thông tin cần thu thập | Điều kiện phải chỉ rõ | Kiểu |
|---|---|---|---|
| `workflow.branching` | Workflow gồm tạo nhánh, ghi cô lập và công bố thay đổi tại cấp đối tượng được chỉ rõ. | `object_scope`, `api` | Trạng thái hỗ trợ |
| `versioning.operation` | Khả năng tạo/sử dụng branch, tag, lịch sử, time travel, merge hoặc rollback theo thao tác và cấp đối tượng. | `reference_type`, `operation`, `object_scope`, `api` | Trạng thái hỗ trợ |

### 8. Federation và migration

Ghi source/provider, thao tác quản lý hay truy vấn, đồng bộ hay tham chiếu trực tiếp và thành phần có thẩm quyền. Migration phải tách data location, table identifier, schema, snapshots và grants; hỗ trợ chuyển một tài sản không tự giữ toàn bộ trạng thái hoặc có đường thoát không mất dữ liệu.

| Property ID | Thông tin cần thu thập | Điều kiện phải chỉ rõ | Kiểu |
|---|---|---|---|
| `metadata.federation_operation` | Quản lý hoặc truy cập metadata từ một loại nguồn qua lớp thống nhất. | `source_type`, `operation`, `api` | Trạng thái hỗ trợ |
| `migration.asset_preservation` | Khả năng chuyển một loại tài sản metadata/dữ liệu giữa scope và catalog khác theo chiều được chỉ rõ. | `direction`, `peer_catalog`, `asset` | Trạng thái hỗ trợ |

### 9. Triển khai, persistence và vận hành

Scope giữ self-managed/managed; nhóm này ghi môi trường được phép/hỗ trợ, dependencies, persistence và tác vụ vận hành. Backup/restore catalog state khác phục hồi cả dữ liệu; HA khác DR; có backend DB không tự chứng minh durability hoặc đạt RTO/RPO.

| Property ID | Thông tin cần thu thập | Điều kiện phải chỉ rõ | Kiểu |
|---|---|---|---|
| `deployment.environment` | Khả năng triển khai hoặc dùng scope trong môi trường được xác định, với deployment mode của scope. | `environment` | Trạng thái hỗ trợ |
| `deployment.dependencies` | Các dịch vụ/phụ thuộc bắt buộc hoặc tùy chọn của scope; note phân biệt hai loại. | Theo scope | Tập giá trị |
| `persistence.backend` | Khả năng dùng một backend lưu trạng thái catalog trong scope được nghiên cứu. | `backend` | Trạng thái hỗ trợ |
| `operations.capability` | Khả năng phục vụ backup/restore, nâng cấp, rollback phiên bản, HA, giám sát hoặc tác vụ vận hành cụ thể. | `operation`, `component` | Trạng thái hỗ trợ |

### 10. Audit, lineage và bảo vệ dữ liệu

Audit và lineage là hai thông tin riêng: cần biết loại sự kiện/quan hệ, boundary, chủ thể và integration. Ghi cơ chế TLS, encryption, secret management/isolation nếu có bằng chứng; không suy tuân thủ pháp lý hay residency từ một tính năng bảo mật.

| Property ID | Thông tin cần thu thập | Điều kiện phải chỉ rõ | Kiểu |
|---|---|---|---|
| `governance.audit` | Ghi nhận một loại sự kiện và chủ thể ở boundary được xác định. | `event_type`, `boundary` | Trạng thái hỗ trợ |
| `governance.lineage` | Thu thập hoặc cung cấp quan hệ lineage được chỉ rõ qua integration cụ thể. | `relation_type`, `integration` | Trạng thái hỗ trợ |
| `security.data_protection` | Khả năng bảo vệ transport, dữ liệu/metadata lưu trữ, secret hoặc isolation theo control và boundary được nêu. | `control`, `boundary` | Trạng thái hỗ trợ |

### 11. Quy mô, chi phí và thông tin dự án

Giữ quota, performance, effort và giá ở đơn vị gốc, kèm nguồn và bối cảnh. Số bảng đã thử không là quota tối đa; OSS không là TCO bằng 0. License, support và project context được lưu để giải thích hoặc kiểm tra chính sách khi liên quan, không tự tạo trọng số/risk score.

| Property ID | Thông tin cần thu thập | Điều kiện phải chỉ rõ | Kiểu |
|---|---|---|---|
| `limits.quota` | Một quota hoặc giới hạn xác định của namespace, bảng, request hoặc tài nguyên khác. | `resource`, `boundary` | Số + đơn vị |
| `performance.observation` | Số đo hiệu năng tại workload, môi trường và loại phép đo được ghi trong observation_context. | `metric`, `scenario` | Số + đơn vị |
| `operations.effort_observation` | Công sức hoặc thời gian của một tác vụ trong điều kiện nhân lực/môi trường cụ thể. | `task`, `scenario` | Số + đơn vị |
| `cost.price_component` | Đơn giá có tiền tệ, đơn vị, thời điểm và tier/điều kiện; không phải TCO hoàn chỉnh. | `component`, `region`, `billing_basis` | Số + đơn vị |
| `project.license` | Các license được nguồn xác nhận cho component/revision thuộc scope. | `component` | Tập giá trị |
| `project.support_policy` | Cam kết hỗ trợ, vòng đời/EOL hoặc hình thức hỗ trợ có nguồn cho đúng provider/edition. | `provider` | Mô tả kỹ thuật |
| `project.maintenance_context` | Thông tin về tổ chức quản trị, release hoặc hoạt động bảo trì được ghi theo thời điểm và phương pháp. | `topic` | Mô tả kỹ thuật |

## 3. Dữ liệu nào dùng kiểu nào?

| Loại dữ liệu | Cách ghi trong claim | Chưa biết |
|---|---|---|
| Khả năng hỗ trợ (`support`) | `level: full/none`; thêm partial chỉ khi property có rubric cho partial | `level: unknown` hoặc chưa có claim |
| Mô tả kỹ thuật (`text`) | `value` là chuỗi mô tả, không tự dùng làm predicate/điểm | `value: null` |
| Tập cơ chế/giấy phép/phụ thuộc (`string_set`) | `value` là mảng chuỗi; ghi note nếu danh sách chưa đầy đủ | `value: null`; mảng rỗng chỉ khi xác nhận thực sự rỗng |
| Quota/số đo/giá (`quantity`) | `value: {amount, unit}` và `observation_context` | `value: null`, không phải 0 hoặc vô hạn |

Ví dụ: RBAC/OIDC là cơ chế cần xác định, không là mức “cao”; 5.000 bảng đã thử là một quan sát, không là giới hạn 5.000; giá dịch vụ không phải điểm chi phí. Các ví dụ số trong câu này chỉ minh họa ngữ nghĩa, không là dữ liệu catalog.

**Rubric hỗ trợ:** full = có căn cứ đáp ứng đúng hợp đồng thuộc tính trong scope/điều kiện; none = có căn cứ không đáp ứng; unknown = chưa đủ tri thức. “Full” không đồng nghĩa mọi chức năng của sản phẩm, đã lab hoặc đạt production.

Chỉ `workflow.branching` có partial ở bản từ điển hiện hành: biết các phần làm được và các phần được xác định không đáp ứng. Nếu mới biết tạo nhánh nhưng chưa biết ghi cô lập/công bố thì kết quả còn unknown, không tự gán partial. Claim partial phải có `covered_parts`, `unmet_parts` và bằng chứng.

Một prerequisite như cấu hình IAM không tự làm tính năng giảm xuống partial. Feature mới là roadmap không được ghi như khả năng đang sẵn có. None/partial/full là thứ bậc kỹ thuật; hàm giá trị/trọng số thuộc [lớp quyết định](complete-kb-selection-method.md), không mặc định 0/0.5/1.

## 4. Cách lưu gọn

Ba collection logic: **scopes**, **properties**, **claims**. Properties dùng chung được tách thành một file để tránh sao lại giữa template và ví dụ; evidence vẫn nhúng trong claim, không dựng hệ thống provenance riêng.

```text
layer-1-properties.json    Định nghĩa 11 nhóm, 37 thuộc tính và rubric
layer-1-template.json      Bộ khung trống để biên soạn scopes/claims
layer-1-example.json       Ví dụ đọc tài liệu, không phải KB đầy đủ
layer-1-data.json          Dữ liệu đã biên soạn cho 7 công nghệ, có evidence nhúng
layer-1-coverage.md        Kiểm kê phần đã thu/chưa thu của 37 thuộc tính
```

Manifest của template/ví dụ có `property_dictionary` chỉ tới file properties, revision, mục đích và limitations. Chỉ một nơi có thẩm quyền cho định nghĩa thuộc tính. Không cần DB hoặc graph để điền lát cắt đầu tiên.

### Scope: thông tin về catalog/biến thể đang mô tả

Trường: `id`, `catalog_id`, `name`, `edition`, `deployment_mode`, và **release** hoặc **as_of**. Thêm provider/region nếu ảnh hưởng kết luận. Release là chuỗi, không có parser range trong v3.

- Scope là phạm vi nghiên cứu, không là manifest cấu hình đầy đủ.
- Một catalog có thể có nhiều scope; không trộn edition/release.
- Các flag/mode/đường truy cập làm đổi tính năng phải có qualifier hoặc giới hạn rõ.
- Cùng scope chưa chứng minh mọi claim cùng hoạt động; tổ hợp cần thêm căn cứ thì giữ kết quả có điều kiện.

### Property: định nghĩa nội dung kỹ thuật

Trường: `id`, `group`, `label`, `definition`, `value_type`, `qualifiers`, `optional_qualifiers`, `interpretation_limits`. Thuộc tính support có `rubric_ref`; quantity có yêu cầu observation context.

`qualifiers` là các chiều bắt buộc để hiểu một claim; `optional_qualifiers` dùng khi nguồn nêu điều kiện hẹp hơn. Không có engine release không nghĩa hỗ trợ mọi release. Không có `form_question`, weight hoặc nice-to-have trong từ điển.

Dictionary v3.1 bổ sung `table_type` và `metadata_representation` dưới dạng qualifier tùy chọn cho `catalog.format_operation`, `integration.engine_operation`, `storage.credential_vending`. Các qualifier này tách managed/foreign và UniForm/Iceberg reads khỏi table format; không thay property ID, kiểu giá trị hoặc rubric. Khi nguồn thu hẹp phạm vi theo chúng thì phải giữ điều kiện đó, không coi vắng qualifier là wildcard.

### Claim: bản ghi tri thức để điền

Trường chung: `id`, `scope_id`, `property_id`, `qualifiers`, **level hoặc value**, `note`, `limits`, `evidence`, `status`.

- Qualifier là các giá trị phân loại so khớp bằng nhau, ví dụ storage=aws_s3 hoặc action=read. Không có ngôn ngữ điều kiện tổng quát.
- Evidence là mảng `{kind, url/path, locator, retrieved_at}`; nhiều claim dẫn cùng URL vẫn không là nguồn độc lập.
- Status mặc định draft. Đọc official doc khác chạy runtime; không lưu workflow phê duyệt nhiều bước hoặc credential thật.
- Dùng level cho support và value cho kiểu còn lại, không ghi hai đáp án có thể mâu thuẫn trong cùng claim.

Quantity đã biết cần có context theo property:
- Quota: loại giới hạn và điều kiện áp dụng.
- Performance: environment, workload, statistic, measurement method.
- Effort: environment, task boundary, measured hay estimated.
- Price: currency, ngày áp dụng, tier, điều kiện; unit phải thể hiện billing basis.

Giá trị text phục vụ giải thích, không là luật máy ngầm. Nếu một yêu cầu bắt buộc phụ thuộc vào mô tả chưa chuẩn hóa thành điều kiện kiểm tra, lớp trên phải báo chưa đánh giá được hoặc biên soạn bổ sung.

## 5. Ví dụ theo đúng miền catalog

[JSON minh họa v3](layer-1-example.json) có **một scope Polaris 1.7.0, sáu claim có căn cứ tài liệu và một claim quota chưa biết**. Ví dụ bao gồm đăng ký bảng Iceberg, xác thực nội bộ/ngoài, RBAC và cấp quyền S3. Nó dùng ba tài liệu chính thức, không phải sáu xác nhận độc lập và không có runtime test.

Các nguồn được đọc chọn lọc ngày 17/10/2026:
- [Polaris Identity Providers](https://polaris.apache.org/releases/1.7.0/managing-security/external-idp/): các authentication mode và đường IdP. Điều kiện mode được giữ riêng trong qualifier.
- [Polaris Access Control](https://polaris.apache.org/releases/1.7.0/managing-security/access-control/): mô hình quyền và table privileges; không suy mức hàng/cột.
- [Polaris Vended Credentials](https://polaris.apache.org/releases/1.7.0/vended-credentials/): cơ chế S3, không lưu khóa cấu hình client hoặc secrets.
- [Trino Iceberg Requirements](https://trino.io/docs/current/connector/iceberg.html#requirements): tham khảo việc tách catalog và storage khi thiết kế nhóm tích hợp.
- [Nessie Transactions](https://projectnessie.org/guides/transactions/): tham khảo việc phân biệt catalog primitive với workflow qua công cụ.

Không lấy “API có TABLE_CREATE” để suy mọi thao tác Iceberg hoặc mọi engine đều được hỗ trợ. Hai claim authentication thuộc mode khác nhau không tự chứng minh chúng đồng thời hoạt động trong một cấu hình. Property chưa có claim là khoảng trống dữ liệu, không phải sản phẩm không hỗ trợ.

## 6. Liên hệ với input đã chốt

Bảng này là tài liệu ranh giới lớp 2; không nhúng ID câu hỏi vào facts.

| Input | Nhóm thông tin lớp 1 liên quan | Cách dùng đúng |
|---|---|---|
| I01 Nơi chạy | Triển khai, tích hợp, storage | Là bối cảnh; không suy cloud = storage hoặc chỉ được chọn vendor đó |
| I02 Engine | Engine/API, authentication, authorization, storage | Kiểm tra đúng engine/thao tác/path; giữ thiếu thông tin về phiên bản hoặc thao tác |
| I03 Format | Format/metadata và engine | Tách quản lý metadata khỏi đọc/ghi; hỗn hợp không tự là mọi format |
| I04 Số bảng | Quota, performance observations | Chỉ lọc/so sánh khi nguồn và bối cảnh đủ; không bịa ngưỡng |
| I05 Engine cùng ghi | Commit/concurrency và integration | Không thay số engine bằng số job hoặc suy transaction nhiều bảng |
| I06 Streaming, nếu giữ | Engine/API/streaming, commit, observations | Kiểm tra mode/path, không một cờ streaming cho mọi catalog |
| I07 Mức quyền | Authorization, authentication; audit khi thực sự cần | Phải rõ enforcement boundary; không tự thêm audit/lineage thành bắt buộc |
| I08 Vending | Storage, authentication, vòng đời credential | Chưa rõ storage thì có điều kiện; vending không là quyền hàng/cột |
| I09 Nền tảng gắn bó | Scope/provider, engine integration, migration, license/support/cost | Hợp đồng của người dùng thuộc hồ sơ ca lựa chọn, không là fact về catalog |
| I10 Nhu cầu đặc thù | Versioning, transaction, federation | Hard/soft và mức chấp nhận do lớp 2–3 quyết định |

Nhóm authentication, persistence hoặc lifecycle vẫn thuộc lớp 1 khi chưa có câu hỏi trực tiếp. Chúng có thể giải thích điều kiện áp dụng của khả năng được hỏi. Một property ngoài form phải có mục tiêu kỹ thuật/giải thích/nghiên cứu rõ, không tự thành tiêu chí cộng điểm.

## 7. Quy ước unknown, điều kiện và dữ liệu trái chiều

1. Không có claim phù hợp → unknown. Nguồn không nhắc tới không chứng minh none; một lỗi lab chưa rõ nguyên nhân cũng không chứng minh không hỗ trợ.
2. Qualifier bắt buộc bị thiếu → chưa đánh giá được; qualifier optional vắng mặt không là wildcard cho một yêu cầu cụ thể chưa được nguồn bao phủ.
3. Hai claim cùng scope/property/qualifiers có đáp án khác nhau → giữ vấn đề cần phân giải, không lấy đa số link hoặc ghi đè im lặng.
4. Không ghép các release, mode hoặc condition loại trừ nhau; không lấy khả năng rời rạc làm bằng chứng tổ hợp end-to-end.
5. Không có miền storage xác định thì không tự tính min–max. Có miền hữu hạn mà còn thiếu claim phải giữ phần unknown; không lấy khoảng chỉ từ các ô đã biết.
6. Không biến số source, số ô full hoặc tỷ lệ kịch bản thắng thành xác suất đúng/điểm phù hợp.
7. Revision bộ dữ liệu và ngày đọc giúp tái lập việc biên soạn; ngày đọc không là ngày lab. Nguồn versioned vẫn có thể thay nội dung, nên lưu snapshot khi cần kiểm chứng chặt hơn.

Quy ước này bảo vệ ý nghĩa dữ liệu; chưa đòi hỏi xây rule engine, version solver hoặc provenance graph. Lớp 3 mới trả PASS/FAIL theo yêu cầu, utility, shortlist và ranking.

## 8. Mức hoàn thành và cách dùng bộ này

**Đã có trong bản v3:** nội dung 11 nhóm; dictionary 37 property với định nghĩa, kiểu và giới hạn; cấu trúc scope/claim; quy ước bằng chứng/unknown; bảng liên hệ input; bộ khung biên soạn; ví dụ tài liệu bao gồm format/authentication/authorization/storage.

**Đã bổ sung dữ liệu ngày 17/10/2026:** [203 claim cho 7 công nghệ](layer-1-data.json), [61 URL chính thức](layer-1-sources.md), [coverage](layer-1-coverage.md) và [kiểm tra dữ liệu](layer-1-data-validation.json). Claim có kết luận vẫn là draft theo tài liệu.

**Chưa có:** dữ liệu đầy đủ cho mọi tổ hợp của 7 công nghệ, xác minh runtime, JSON Schema/evaluator/inference và thang giá trị/trọng số đã xác nhận. Script kiểm tra cấu trúc dữ liệu không thay JSON Schema hoặc engine lựa chọn. V3 không tự mở rộng form hoặc tạo thêm tiêu chí mềm.

Có thể bắt đầu điền theo từng catalog bằng cùng từ điển, ưu tiên những claim dùng trực tiếp cho input rồi bổ sung điều kiện kỹ thuật cần để hiểu chúng. Không cần điền 37 × mọi engine × mọi storage. Nếu lát cắt không đòi hỏi performance/TCO, giữ nhóm quan sát chưa điền thay vì tự cho điểm.

Khác v2: giữ evidence nhúng, scope đơn giản và exact qualifiers; bổ sung nội dung miền và value types. Những property ID còn cùng nghĩa được giữ; một số ID mô tả rộng hơn có thể đổi. Dữ liệu cũ phải đối chiếu hợp đồng mới, không tự chuyển boolean thành full hoặc chuỗi mô tả thành điểm.

Bản thiết kế và các rubric là đề xuất riêng cho đề tài; nguồn sản phẩm giúp kiểm tra ví dụ và các ranh giới cần mô hình hóa, không chứng minh danh mục này bao phủ mọi tình huống ngoài thực tế.

Kiểm tra artifact đã thực hiện: ba file JSON parse được; 11 group và 37 property có ID/reference hợp lệ; mọi property xuất hiện trong tài liệu; 7 claim mẫu có kiểu/qualifier/evidence đúng quy ước; level không trộn vào value, unknown nằm ngoài thang thứ bậc; không trùng khóa claim; tham chiếu dictionary và liên kết nội bộ tồn tại. Không phát hiện lỗi trong các kiểm tra này. Đây là kiểm tra cấu trúc, không phải chạy schema/inference hoặc kiểm thử chức năng các catalog.

