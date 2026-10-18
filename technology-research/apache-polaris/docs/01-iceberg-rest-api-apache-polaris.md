# Chương 1 — Iceberg REST API trong kiến trúc Apache Polaris

*Ngày nghiên cứu: 02-09-2026 · Phạm vi: API/Protocol Layer → Iceberg REST API, kèm các điểm giao bắt buộc sang Security, Catalog Service, Metadata, Persistence, Storage và Supporting Subsystems.*

## 1. Kết luận kiến trúc

Iceberg REST API trong Polaris không phải một controller CRUD độc lập. Nó là mặt giao thức bên ngoài của một pipeline xuyên gần như toàn bộ Polaris Server:

```text
Iceberg client / Spark / Flink / Trino / PyIceberg
  │
  │ HTTP: /api/catalog/v1/...
  ▼
Generated JAX-RS API từ OpenAPI
  ▼
Realm + Authentication
  ▼
IcebergRest*EventServiceDelegator
  ▼
IcebergCatalogAdapter
  ▼
IcebergCatalogHandler
  ├── Entity Resolution + RBAC
  ├── LocalIcebergCatalog ──► BasePolarisTableOperations
  └── Federated Iceberg REST Catalog
  ▼
PolarisMetaStoreManager ──► in-memory / relational-jdbc / NoSQL
  │
  └── FileIO + S3/Azure/GCS + credential vending
```

Điểm cần nhớ nhất:

1. **REST server không lưu toàn bộ Iceberg metadata trong database.** Metastore lưu entity, hierarchy, quyền, properties và con trỏ `metadataLocation`; file `metadata.json`, manifests và data vẫn nằm ở storage.
2. **Commit không gửi lại toàn bộ metadata.** Client gửi `requirements` và `updates`; server kiểm tra optimistic concurrency, tạo metadata mới, ghi file mới, rồi CAS con trỏ trong metastore.
3. **Đường REST chỉ là lớp đầu.** Mỗi operation đều phải resolve realm, principal, active roles, catalog path, privilege, storage location và persistence transaction.
4. **Polaris không triển khai toàn bộ living spec của Iceberg.** Polaris chọn tập endpoint được expose trong OpenAPI hợp nhất của riêng dự án.

Nguồn lõi: [Iceberg REST Catalog Spec](https://iceberg.apache.org/rest-catalog-spec/), [Iceberg OpenAPI](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml), [Polaris catalog OpenAPI](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/spec/polaris-catalog-service.yaml), [Polaris source](https://github.com/apache/polaris/tree/9da600803a540ae168580053c952f8ac6c947986).

## 2. Mốc phiên bản phải phân biệt

### 2.1 Iceberg

- Release ổn định mới nhất khi nghiên cứu là **Apache Iceberg 1.11.0**, phát hành tháng 05-2026. Bản OpenAPI đóng băng theo release nằm tại [tag `apache-iceberg-1.11.0`](https://github.com/apache/iceberg/blob/apache-iceberg-1.11.0/open-api/rest-catalog-open-api.yaml).
- File trên `main` là **living specification**. Nó vẫn khai báo `openapi: 3.1.1`, `info.version: 0.0.1` và route `/v1`; con số `0.0.1` không phải phiên bản thư viện Iceberg và không phản ánh đầy đủ lịch sử tiến hóa của protocol.
- `main` hiện có thêm ba path so với 1.11.0: list/load SQL functions và unregister table.

### 2.2 Polaris

- Release ổn định mới nhất là **Polaris 1.7.0**, phát hành 02-08-2026 theo [trang tải chính thức](https://polaris.apache.org/downloads/).
- Phân tích source trong tài liệu này dùng `main` commit [`9da600803a540ae168580053c952f8ac6c947986`](https://github.com/apache/polaris/commit/9da600803a540ae168580053c952f8ac6c947986), ngày 01-09-2026. Đây là mã mới hơn 1.7.0, nên một vài logic như idempotency trên `main` có thể chưa có trong binary 1.7.0.
- Bản Iceberg OpenAPI được copy vào Polaris ghi rõ **Iceberg 1.11.0**, commit upstream `6976e020...`: [file copy trong Polaris](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/spec/iceberg-rest-catalog-open-api.yaml).

Do đó, câu “Polaris hỗ trợ Iceberg REST v1” chưa đủ chính xác. Cần nói rõ: **Polaris release/commit nào, baseline Iceberg nào và endpoint nào được quảng bá qua `/config`.**

## 3. Vai trò của Iceberg REST Catalog protocol

REST Catalog là protocol giữa compute engine/client và catalog service. Nó giải quyết việc mỗi engine/ngôn ngữ phải cài một catalog plugin riêng bằng cách chuẩn hóa:

- bootstrap configuration và capability negotiation;
- namespace/table/view lifecycle;
- change-based optimistic commits;
- lazy snapshot loading và cache validation;
- atomic multi-table commits;
- credential vending hoặc remote signing;
- metrics và server-side scan planning.

Catalog server quản lý **root metadata pointer** và catalog atomicity. Client vẫn dùng `FileIO` để đọc/ghi data files, manifest files và thường cả metadata files bằng quyền storage được cấp. Đây là lý do Iceberg REST API nằm ở API layer nhưng commit thực tế xuyên xuống Storage Integration và Persistence. [Apache mô tả các mục tiêu protocol tại đây](https://iceberg.apache.org/rest-catalog-spec/).

## 4. Bootstrap: `/config`, `warehouse`, `prefix` và capabilities

### 4.1 Luồng chuẩn của Iceberg client

1. Client dựng HTTP/auth tạm thời từ cấu hình local.
2. Gọi `GET /v1/config?warehouse=...` — route này chưa có `{prefix}`.
3. Merge cấu hình theo thứ tự:

   ```text
   server defaults → client properties → server overrides
   ```

4. Lấy `prefix`, `namespace-separator`, `endpoints`, auth/storage properties và `idempotency-key-lifetime`.
5. Tạo catalog session cuối cùng.
6. Các operation tiếp theo dùng `/v1/{prefix}/...`.

Java reference client hiện thực luồng này trong [`RESTSessionCatalog.initialize`](https://github.com/apache/iceberg/blob/main/core/src/main/java/org/apache/iceberg/rest/RESTSessionCatalog.java#L185).

### 4.2 Polaris xử lý `/config`

Polaris có public base path `/api/catalog`, vì OpenAPI Generator được cấu hình `serverVariables.basePath = api/catalog`: [`api/iceberg-service/build.gradle.kts`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/api/iceberg-service/build.gradle.kts#L63-L127).

URL thực tế:

```http
GET /api/catalog/v1/config?warehouse=my_catalog
```

`IcebergCatalogAdapter.getConfig` bắt buộc `warehouse`; thiếu giá trị trả `400`, dù tham số này là optional trong upstream OpenAPI. Adapter xác thực principal rồi gọi `CatalogConfigHandler`: [adapter](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogAdapter.java#L765-L775).

`CatalogConfigHandler`:

- resolve catalog/warehouse theo principal;
- trả catalog properties trong `defaults`;
- ép `overrides.prefix` về prefix canonical của Polaris;
- ép `namespace-separator=%1F`;
- hợp nhất danh sách endpoint từ các CDI contributor;
- quảng bá `idempotency-key-lifetime` nếu feature được bật.

Nguồn: [`CatalogConfigHandler`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/config/CatalogConfigHandler.java#L67-L110), [`IcebergRestConfigEndpoints`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergRestConfigEndpoints.java), [`IcebergViewConfigEndpoints`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergViewConfigEndpoints.java).

### 4.3 Phân biệt `basePath` và `{prefix}`

- `basePath`: `/api/catalog`, thuộc deployment/HTTP server.
- `{prefix}`: tên catalog đã canonicalize, đứng sau `/v1`.
- `warehouse`: input dùng để tìm catalog trong `/config`.
- `prefix`: output do server quyết định cho các request sau.

Ví dụ:

```text
base URL      = https://polaris.example.com/api/catalog
warehouse     = analytics
prefix trả về = analytics
table URL     = /api/catalog/v1/analytics/namespaces/prod/tables/events
```

### 4.4 Capability negotiation

`CatalogConfig.endpoints` chứa chuỗi dạng `<METHOD> <OpenAPI path>`. Client phải dựa vào danh sách này, không nên suy đoán capability. Nếu field vắng mặt, Iceberg client chỉ giả định tập endpoint legacy mặc định; view, HEAD-exists, credentials, signing, planning, functions và unregister không mặc nhiên được hỗ trợ. [Tập mặc định của Java client](https://github.com/apache/iceberg/blob/main/core/src/main/java/org/apache/iceberg/rest/RESTSessionCatalog.java#L118).

## 5. Endpoint matrix: Iceberg so với Polaris

Mọi path catalog-scoped dưới đây có tiền tố `/api/catalog/v1/{prefix}` trong Polaris.

| Nhóm | Method/path | Polaris `main` | Ghi chú |
|---|---|---:|---|
| Config | `GET /v1/config` | Có | Polaris bắt buộc `warehouse` |
| OAuth cũ | `POST /v1/oauth/tokens` | Có | Iceberg đánh dấu deprecated; Polaris giữ cho internal auth |
| Namespace | `GET, POST /namespaces` | Có | List/create |
| Namespace | `GET, HEAD, DELETE /namespaces/{ns}` | Có | Load/exists/drop |
| Namespace | `POST /namespaces/{ns}/properties` | Có | Upsert/remove properties |
| Table | `GET, POST /namespaces/{ns}/tables` | Có | List/create; `stage-create` hỗ trợ |
| Table | `POST /namespaces/{ns}/register` | Có | Register metadata đã tồn tại |
| Table | `GET, HEAD, POST, DELETE /.../tables/{table}` | Có | Load/exists/commit/drop |
| Table | `GET /.../tables/{table}/credentials` | Có | Refresh vended credentials |
| Table | `POST /tables/rename` | Có | Rename/move |
| Metrics | `POST /.../tables/{table}/metrics` | Có | Scan/commit metrics |
| Transaction | `POST /transactions/commit` | Có | Atomic multi-table commit nội bộ |
| View | `GET, POST /namespaces/{ns}/views` | Có | List/create |
| View | `POST /namespaces/{ns}/register-view` | Có | Register view metadata |
| View | `GET, HEAD, POST, DELETE /.../views/{view}` | Có | Load/exists/replace/drop |
| View | `POST /views/rename` | Có | Rename/move |
| Scan planning | `/plan`, `/plan/{id}`, `/tasks` | Không | Polaris OpenAPI ghi rõ chưa triển khai |
| Remote signing | `POST /.../tables/{table}/sign` | Không | Enum/resolver có nhưng handler vẫn reject `remote-signing` |
| SQL function | `/functions`, `/functions/{function}` | Không | Mới trên Iceberg `main`, sau baseline 1.11 |
| Unregister | `POST /.../tables/{table}/unregister` | Không | Mới trên Iceberg `main` |

Tập endpoint chính xác mà Polaris expose nằm trong [`spec/polaris-catalog-service.yaml`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/spec/polaris-catalog-service.yaml#L62-L160).

## 6. Các lớp thực thi trong Polaris

### 6.1 Generated JAX-RS API

Polaris dùng OpenAPI Generator `jaxrs-resteasy` để sinh resource/interface `IcebergRestCatalogApiService`, `IcebergRestConfigurationApiService` và OAuth API. Request/response model phần lớn map sang type của `org.apache.iceberg.rest.*`. Điều này giữ wire model gần Java Iceberg SDK nhưng cũng khiến việc cập nhật baseline Iceberg phải được kiểm soát cẩn thận. [Cấu hình generator](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/api/iceberg-service/build.gradle.kts).

### 6.2 Event decorator

`IcebergRestCatalogEventServiceDelegator` là CDI decorator quanh adapter. Nó phát `BEFORE_*`, gọi delegate, rồi phát `AFTER_*` khi thành công. Multi-table transaction còn phát event update cho từng table. Đây là điểm giao sang chương **Supporting Subsystems → Events**. [Source](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergRestCatalogEventServiceDelegator.java).

### 6.3 `IcebergCatalogAdapter`

Adapter chịu trách nhiệm HTTP/protocol:

- parse namespace/path/header/query;
- validate request model, entity name và Iceberg properties;
- loại reserved properties không cho client ghi trực tiếp;
- parse `X-Iceberg-Access-Delegation`;
- xử lý ETag/`If-None-Match`;
- phân nhánh direct create và staged create;
- map domain result sang HTTP `Response`.

Adapter không chứa persistence logic. Mỗi request tạo một `IcebergCatalogHandler`, thực thi rồi đóng catalog/FileIO: [source](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogAdapter.java#L73-L135).

### 6.4 `IcebergCatalogHandler`

Handler là application service của Iceberg REST:

- dựng resolution manifest;
- kiểm tra authorization intent;
- chọn local hay federated catalog;
- áp business rules của Polaris;
- quyết định privilege cho từng operation/update;
- điều phối credential vending;
- điều phối single-table và multi-table commit.

Factory inject vào handler diagnostics, call context, resolver, metastore manager, authorizer, credential manager, storage access provider, event attributes, metrics, clock và idempotency context: [`IcebergCatalogHandlerFactory`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandlerFactory.java).

### 6.5 `LocalIcebergCatalog`

Đây là bridge từ Iceberg Catalog API sang Polaris entity/metastore:

- namespace CRUD;
- table/view list/register/drop/rename;
- default location và location validation;
- tạo `TableOperations`/`ViewOperations`;
- gọi `PolarisMetaStoreManager` để create/update/drop/list entity.

Catalog nội bộ dùng `LocalIcebergCatalog`; catalog external dùng `FederatedCatalogFactory` và Iceberg SDK `RESTCatalog`. [Khởi tạo trong handler](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandler.java#L211-L268).

### 6.6 `BasePolarisTableOperations`

Đây là lớp quyết định semantics của table refresh/commit:

- `refresh`: đọc fresh entity từ metastore, lấy `metadataLocation`, dựng FileIO và đọc metadata JSON;
- `commit`: từ chối stale base, gọi `doCommit`, chỉ cập nhật in-memory state sau khi persistence thành công;
- `doCommit`: validate namespace/location, ghi metadata file mới, so sánh con trỏ cũ, CAS entity, cleanup file mới nếu thất bại.

Nguồn: [`BasePolarisTableOperations`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/LocalIcebergCatalog.java#L1714-L2058).

## 7. Namespace logic

Namespace trong JSON là array, ví dụ `['accounting','tax']`; trong URL các level nối bằng byte unit separator `0x1F`, URL-encoded `%1F`. Polaris luôn quảng bá separator mặc định này.

### List

- Không có `parent`: trả namespace top-level.
- Có parent: trả trực tiếp các namespace con một cấp.
- Local catalog dùng metastore pagination; federated catalog delegate xuống catalog ngoài.

### Create

1. Adapter validate namespace và properties.
2. Handler yêu cầu `NAMESPACE_CREATE` trên parent; root namespace là implicit nên không được create.
3. Local catalog resolve parent, tính location mặc định, kiểm tra custom-location và overlap.
4. Tạo `NamespaceEntity` bằng `createEntityIfNotExists`.
5. Duplicate trả `409`.

[Namespace handler](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandler.java#L270-L375), [local namespace implementation](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/LocalIcebergCatalog.java#L651-L1006).

### Update properties

Request có `updates` và `removals`. Adapter loại reserved keys. Local catalog dùng optimistic entity update; concurrent modification thành conflict. Key vừa update vừa remove là semantic error `422` theo spec.

### Drop

Namespace chỉ được xóa khi rỗng. Còn child namespace/table/view thì `NamespaceNotEmptyException` → `409`.

## 8. Table create: direct và staged/CTAS

### 8.1 Direct create

Request bắt buộc `name`, `schema`; có thể có `location`, partition spec, sort order, properties và access delegation.

Flow Polaris:

1. Adapter validate request, properties và identifier.
2. Handler resolve catalog và authorize:
   - không delegation: `TABLE_CREATE`;
   - cần write delegation: `TABLE_CREATE + TABLE_WRITE_DATA`.
3. Reject static-facade external catalog.
4. Kiểm tra idempotency replay nếu feature bật.
5. Kiểm tra table/view cùng tên đã tồn tại.
6. Kiểm tra client-specified location và allowed locations.
7. Dùng Iceberg `TableBuilder.create()`.
8. `BasePolarisTableOperations.doCommit` ghi metadata JSON và tạo entity.
9. Trả `LoadTableResponse`, ETag và credential/config nếu yêu cầu.

[Direct create source](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandler.java#L378-L512).

### 8.2 Staged create

`stage-create=true` phục vụ atomic CTAS/RTAS:

1. Polaris authorize create nhưng **chưa tạo table entity**.
2. Server xây `TableMetadata` chưa committed; `metadata-location` có thể null.
3. Nếu client xin delegation, Polaris có thể cấp quyền storage để client ghi data/metadata staging.
4. Client hoàn tất bằng `POST .../tables/{table}` với requirement `assert-create` và ordered updates.
5. Adapter nhận diện `AssertTableDoesNotExist` qua `CatalogHandlerUtils.isCreate` và đi vào `updateTableForStagedCreate`.
6. Commit thành công mới làm table visible trong catalog.

[Staged create source](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandler.java#L604-L690), [`isCreate`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/CatalogHandlerUtils.java#L327-L390).

## 9. Register, load, cache và drop table

### Register

`register` không tạo metadata từ schema. Nó đọc metadata JSON đã tồn tại tại `metadata-location`, validate location, rồi tạo catalog pointer/entity. `overwrite=false` mặc định; Polaris chỉ hỗ trợ overwrite cho catalog nội bộ, không hỗ trợ federated. [Source](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandler.java#L702-L741).

### Load

1. Resolve table và authorize `TABLE_READ_PROPERTIES`.
2. Nếu xin vended credentials, thử write privilege trước; fallback read privilege.
3. Nếu `If-None-Match` match ETag hiện tại, trả `304`.
4. `LocalIcebergCatalog` đọc entity fresh từ metastore để lấy `metadataLocation`.
5. FileIO đọc `metadata.json`.
6. `snapshots=refs` loại historical snapshots không được ref tham chiếu; `all` trả đầy đủ.
7. Validate mọi location hiện tại trước khi cấp credential.
8. Trả metadata, config, storage credentials và ETag.

[Load handler](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandler.java#L1030-L1188).

Polaris tạo weak ETag bằng SHA-256 của `metadata-location`: [`IcebergHttpUtil`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/http/IcebergHttpUtil.java). `If-None-Match: *` bị adapter từ chối.

### Drop và purge

- `purgeRequested=false`: bỏ catalog entity/pointer, không chủ động xóa toàn bộ data.
- `purgeRequested=true`: yêu cầu `TABLE_DROP + TABLE_WRITE_DATA`, chịu feature gate và chạy cleanup files.
- Static-facade external catalog không cho purge mutation.

Iceberg `main` còn có `unregister`, nhưng Polaris baseline và API hợp nhất hiện chưa expose endpoint này.

## 10. Single-table commit: logic đầy đủ

Wire request:

```json
{
  "requirements": [
    {"type": "assert-table-uuid", "uuid": "..."},
    {"type": "assert-ref-snapshot-id", "ref": "main", "snapshot-id": 123}
  ],
  "updates": [
    {"action": "add-snapshot", "snapshot": {}},
    {"action": "set-snapshot-ref", "ref-name": "main", "snapshot-id": 456}
  ]
}
```

Requirements là điều kiện optimistic-concurrency: assert create, table UUID, ref snapshot ID, current schema ID, last assigned field/partition ID, default spec ID và default sort-order ID. Updates là ordered changes: schema/spec/sort order/snapshot/ref/location/properties/statistics/encryption keys. [Danh sách canonical nằm trong OpenAPI](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml).

### 10.1 Adapter

- validate `SetProperties`;
- loại reserved property updates;
- tạo `UpdateTableRequest` domain;
- nếu có `assert-create`, chuyển sang staged-create finalization; ngược lại gọi normal update.

### 10.2 Handler và RBAC

Handler resolve target một lần rồi suy ra privilege. Khi fine-grained update privilege bật, từng `MetadataUpdate` map sang privilege riêng như add schema, add snapshot, set location, set properties; khi tắt, dùng `TABLE_WRITE_PROPERTIES`. [Mapping trong handler](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandler.java#L1638-L1702).

### 10.3 `CatalogHandlerUtils.commit`

1. Lấy current metadata.
2. Validate mọi requirement trên base.
3. Requirement fail là deterministic conflict; không server-retry vô ích.
4. Apply ordered updates vào `TableMetadata.Builder`.
5. Nếu không có change, kết thúc không ghi.
6. Gọi `TableOperations.commit(base, updated)`.
7. Nếu persistence conflict có thể retry, refresh metadata và exponential backoff đến giới hạn cấu hình.
8. Mỗi lần retry phải validate requirement lại trên fresh base.

[Commit algorithm](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/CatalogHandlerUtils.java#L394-L523).

### 10.4 `BasePolarisTableOperations.doCommit`

1. Reject `base != current()` như stale metadata.
2. Xác minh namespace vẫn tồn tại.
3. Resolve fresh table entity và storage entity.
4. Thu thập table/data/metadata locations cần dùng.
5. Validate allowed locations, không overlap table khác, metadata file nằm đúng table directory.
6. Dựng FileIO với READ/WRITE/LIST.
7. Ghi metadata JSON mới với filename version + UUID.
8. So sánh stored current `metadataLocation` với old location mà request dựa trên — CAS lớp 1.
9. Gọi `updateEntityPropertiesIfNotChanged` — CAS/version lớp 2 ở metastore.
10. Chỉ sau persistence success mới cập nhật in-memory current metadata.
11. Nếu thất bại sau khi đã ghi file mới, xóa file mới để tránh orphan.

Vì vậy atomic point của table là **swap pointer trong metastore**, còn metadata file được tạo trước. Cleanup bù trừ bảo đảm thất bại không để con trỏ dangling. [Source](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/LocalIcebergCatalog.java#L1902-L2058).

### 10.5 Kết quả conflict

- Requirement hoặc CAS conflict → `409 CommitFailedException`/`CommitConflictException`.
- Client refresh metadata, rebase change và retry.
- Commit-state-unknown `500/502/504` phải được xử lý khác: không tùy tiện tạo commit mới; reload state hoặc retry cùng idempotency key nếu được quảng bá.

## 11. Atomic multi-table transaction

Endpoint: `POST /api/catalog/v1/{prefix}/transactions/commit`.

Flow Polaris:

1. Adapter validate và lọc reserved properties trong mọi table change.
2. Handler authorize toàn bộ collection.
3. Reject federated catalog, static facade và staged-create nằm trong transaction.
4. Thay metastore manager của `LocalIcebergCatalog` bằng `TransactionWorkspaceMetaStoreManager`.
5. Group changes theo table, giữ insertion order.
6. Với mỗi table, load một base metadata.
7. Nếu một table xuất hiện nhiều lần, validate/apply tuần tự trên evolving metadata nhưng coalesce thành một `tableOps.commit`.
8. Metadata JSON mới được ghi ra storage; entity updates chỉ nằm trong workspace.
9. Cuối cùng gọi một lần `updateEntitiesPropertiesIfNotChanged(pendingUpdates)` để CAS toàn bộ pointer như một unit.
10. Nếu atomic metastore update fail, xóa tất cả metadata file mới và trả conflict.
11. Nếu success, mới chạy delete-removed-metadata cleanup.

[Implementation đầy đủ](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandler.java#L1340-L1502).

Giới hạn quan trọng: đây là atomicity của **catalog pointers trong metastore**. Object-store writes xảy ra trước và được bù bằng cleanup khi transaction fail. Federated REST catalog không được hỗ trợ bởi transaction này.

## 12. Views

View dùng pipeline tương tự table nhưng model khác:

- create: schema, view-version, SQL representations, default catalog/namespace, properties/location;
- load: `ViewMetadata` + metadata location;
- replace: `assert-view-uuid` + view updates;
- register, list, exists, drop, rename;
- `BasePolarisViewOperations` ghi view metadata JSON và CAS pointer/entity tương tự table.

Polaris dùng privilege `VIEW_CREATE`, `VIEW_READ_PROPERTIES`, `VIEW_WRITE_PROPERTIES`, `VIEW_DROP`, `VIEW_LIST`. Table và view dùng chung namespace tên; cùng identifier không thể đồng thời tồn tại. [View handler](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandler.java#L1518-L1610), [view commit](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/LocalIcebergCatalog.java#L2367-L2484).

## 13. Security boundary của Iceberg REST request

Đây là phần giao sang chương **Security Layer**, không phải toàn bộ Security chapter.

```text
Polaris-Realm
  → resolve RealmContext
Bearer/OIDC token
  → resolve principal
requested PRINCIPAL_ROLE scopes
  → chỉ activate role thật sự đã grant
catalog prefix + object path
  → Resolver tạo target path
operation
  → RbacOperationSemantics chọn privilege
PolarisAuthorizerImpl
  → allow / 403
```

### Realm

Realm là biên multitenancy cho resource, credentials, config và persistence. `RealmContextFilter` chạy trước endpoint; realm thiếu/không hợp lệ trả Iceberg error. Trong production nên bắt buộc header thay vì fallback realm đầu tiên. [Stable realm docs](https://polaris.apache.org/releases/1.7.0/realm/).

### Authentication và scope

Internal token endpoint thực tế:

```http
POST /api/catalog/v1/oauth/tokens
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
client_id=...
client_secret=...
scope=PRINCIPAL_ROLE:ALL
```

Polaris chỉ chấp nhận `client_credentials` và OAuth token-exchange grant. Scope client credentials là bắt buộc và phải có dạng `PRINCIPAL_ROLE:<name>`; nhiều role cách nhau bằng space. `PRINCIPAL_ROLE:ALL` nghĩa mọi principal role mà principal **thực sự được grant**, không phải superuser scope. [OAuth service](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/internal/service/DefaultOAuth2ApiService.java), [validator](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/internal/broker/TokenRequestValidator.java), [authenticator](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/DefaultAuthenticator.java).

Iceberg upstream đã deprecate token endpoint tích hợp và khuyến nghị external authorization server; Polaris vẫn giữ endpoint vì internal authentication mode cần nó.

### RBAC mapping chính

| Operation | Privilege chính |
|---|---|
| List namespace/table | `NAMESPACE_LIST` / `TABLE_LIST` |
| Load table metadata | `TABLE_READ_PROPERTIES` |
| Create/staged create | `TABLE_CREATE` |
| Create + write credentials | `TABLE_CREATE + TABLE_WRITE_DATA` |
| Load + read credentials | `TABLE_READ_DATA` |
| Load + write credentials | `TABLE_WRITE_DATA` |
| Update table | Fine-grained update privilege hoặc `TABLE_WRITE_PROPERTIES` |
| Drop | `TABLE_DROP` |
| Purge | `TABLE_DROP + TABLE_WRITE_DATA` |
| Rename | Source `TABLE_DROP`; destination `TABLE_LIST + TABLE_CREATE` |
| Multi-table commit | `TABLE_WRITE_PROPERTIES + TABLE_CREATE` |
| Read/write metrics | `TABLE_READ_DATA` / `TABLE_WRITE_DATA` |

Canonical mapping: [`RbacOperationSemantics`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/RbacOperationSemantics.java), [stable access-control docs](https://polaris.apache.org/releases/1.7.0/managing-security/access-control/).

## 14. Credential vending và storage integration

Client yêu cầu:

```http
X-Iceberg-Access-Delegation: vended-credentials
```

Flow:

1. Handler resolve table và privileges.
2. Thử `TABLE_WRITE_DATA`: nếu có, vend READ/LIST/WRITE.
3. Nếu không, thử `TABLE_READ_DATA`: vend READ/LIST.
4. Lấy tất cả actual table/data/metadata locations.
5. Kiểm tra chúng vẫn nằm trong current catalog allowed locations.
6. Tạo location-scoped access grant.
7. Storage integration tạo credential ngắn hạn:
   - S3: STS AssumeRole + scoped session policy;
   - Azure: user-delegation SAS theo container/path;
   - GCS: downscoped OAuth token/Credential Access Boundary.
8. Trả credential trong `storage-credentials`/`credentials`, cùng refresh endpoint.

`GET .../credentials` có fast path đọc location từ entity internal properties, tránh load toàn bộ metadata; nếu thiếu data hoặc catalog federated thì fallback full load. Mỗi refresh vẫn re-authorize và re-validate location. [Handler](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandler.java#L815-L1188), [stable credential docs](https://polaris.apache.org/releases/1.7.0/vended-credentials/).

### Remote signing hiện chưa hoàn tất

Source có enum và resolver cho `remote-signing`, nhưng `IcebergCatalogHandler.resolveAccessDelegationModes` vẫn chủ động reject mode này với TODO. Polaris OpenAPI hợp nhất cũng không expose `/sign`. Vì vậy, trên code snapshot đã đọc, cơ chế production thực tế là vended credentials. [Resolver](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/DefaultAccessDelegationModeResolver.java), [handler reject](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandler.java#L1712-L1728).

## 15. Federation

Với catalog external có connection config, handler không tạo `LocalIcebergCatalog` mà chọn `FederatedCatalogFactory`. Iceberg REST federation dùng Iceberg SDK `RESTCatalog` làm outbound client.

```text
Engine → Polaris Iceberg REST
          ├── local realm/auth/RBAC vẫn áp dụng
          └── Polaris → remote Iceberg REST catalog
                        └── outbound OAuth/Bearer/SigV4/GCP auth
```

Giới hạn source hiện tại:

- feature disabled mặc định;
- không native local pagination/location transformation/multi-table transaction;
- register overwrite chỉ hỗ trợ internal catalog;
- generic tables không được federation theo đường Iceberg REST này;
- remote error/unsupported behavior có thể được truyền về client.

[Stable federation docs](https://polaris.apache.org/releases/1.7.0/federation/iceberg-rest-federation/), [`IcebergRESTFederatedCatalogFactory`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergRESTFederatedCatalogFactory.java).

## 16. Pagination

Iceberg protocol dùng `pageToken`, `pageSize`, response `next-page-token`. Client bắt đầu pagination bằng token rỗng, rồi coi token server trả là opaque cho đến khi null/missing.

Polaris local pagination:

- feature `LIST_PAGINATION_ENABLED` mặc định tắt;
- khi bật, token là URL-safe Base64 của Smile-serialized backend token;
- token giữ page size và backend continuation state;
- common token hiện chưa có cryptographic signature; source có TODO cho signature;
- khi tắt, local handler đọc toàn bộ;
- federated path hiện list remote rồi slice bằng integer offset helper thay vì native Polaris token.

[PageToken](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/persistence/pagination/PageToken.java), [PageTokenUtil](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/persistence/pagination/PageTokenUtil.java).

## 17. Idempotency trên Polaris `main`

Upstream Iceberg quy định `Idempotency-Key` là UUIDv7 và `/config` quảng bá lifetime. Polaris `main`:

- feature mặc định `false`, TTL mặc định `PT5M`;
- filter parse header bằng `UUID.fromString`, tức nhận UUID hợp lệ nói chung, không kiểm tra riêng version 7;
- key được ghi atomically vào internal properties của table entity;
- create/update table có replay logic nếu key còn sống;
- key window không dùng idempotency store riêng.

[Configuration](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/idempotency/IdempotencyConfiguration.java), [filter](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/idempotency/IdempotencyKeyFilter.java), [entity model](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/idempotency/EntityIdempotency.java).

Lưu ý: OpenAPI Iceberg mô tả replay cho mutation endpoints nói chung, trong khi source snapshot cho thấy replay logic cụ thể tập trung ở direct create/update table. Vì feature mặc định tắt và code mới hơn 1.7.0, cần chạy compatibility/integration test trước khi bật với kỳ vọng idempotency toàn API.

## 18. Error mapping

Polaris trả Iceberg error envelope:

```json
{
  "error": {
    "message": "...",
    "type": "CommitFailedException",
    "code": 409
  }
}
```

| Exception/condition | HTTP |
|---|---:|
| Namespace/table/view not found | 404 |
| Already exists, commit conflict, namespace not empty | 409 |
| Invalid JSON/value/argument/validation | 400 |
| Not authenticated | 401 |
| Authenticated nhưng thiếu privilege | 403 |
| Unsupported operation | 406 |
| Unprocessable semantic request | 422 |
| Timeout | 408 |
| Service/storage unavailable | 503 |
| Commit state unknown/unhandled | 500 |
| Cloud access denied | 403 |
| Cloud provider 5xx | 502 |

[`IcebergExceptionMapper`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/exception/IcebergExceptionMapper.java), [`IcebergJsonProcessingExceptionMapper`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/exception/IcebergJsonProcessingExceptionMapper.java).

OAuth endpoint là ngoại lệ: lỗi dùng OAuth error JSON thay vì Iceberg envelope.

## 19. Metrics, events và cleanup

### Metrics

`POST .../metrics` nhận scan report hoặc commit report. Handler phân quyền read/write data, lấy catalog/table IDs từ resolved entities rồi gửi envelope cho `IcebergMetricsReporter`. Đây là metrics của client operation, khác HTTP/server metrics. [Source](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/metrics/IcebergMetricsReporter.java).

### Events

Event decorator phát before/after cho config, namespace, table, view và transaction. Vì after event chỉ chạy sau delegate thành công, listener thấy state đã committed; multi-table transaction còn gắn metadata list thông qua request-scoped event attribute map.

### Cleanup

- Single commit fail sau khi ghi file mới: xóa new metadata file.
- Multi-table atomic update fail: xóa tất cả new metadata files từ pending updates.
- Commit success: mới xóa removed metadata files nếu table config bật cleanup.
- Drop with purge: cleanup data/metadata theo Iceberg catalog behavior và Polaris feature gates.
- Background table cleanup là subsystem riêng; REST handler chỉ kích hoạt/điều phối một số cleanup đồng bộ.

## 20. Các khác biệt và điểm cần kiểm chứng

### 20.1 Khác biệt chắc chắn từ source

1. **Scan planning chưa expose** dù có trong Iceberg 1.11 OpenAPI.
2. **Remote signing chưa triển khai end-to-end**; handler reject mode.
3. **Functions và unregister chưa có** vì là bổ sung sau Iceberg 1.11 baseline.
4. **`warehouse` optional trong spec nhưng bắt buộc ở Polaris `/config`.**
5. **Federated catalog không hỗ trợ Polaris multi-table atomic commit.**
6. **Pagination local mặc định tắt.**
7. **Idempotency mặc định tắt và UUID version không được enforce ở filter.**

### 20.2 Compatibility nuance

- Spec khuyến nghị ETag khác nhau khi cùng metadata version nhưng response representation khác nhau, ví dụ `snapshots=refs` và `all`. Polaris ETag chỉ hash `metadata-location`, nên hai representation có thể có cùng ETag.
- Polaris copy Iceberg 1.11 mô tả access-delegation như comma-separated list nhưng schema cũ khai báo string enum; parser Polaris thực tế split comma và còn hỗ trợ legacy `true`.
- Credential refresh endpoint tồn tại nhưng không nằm trong core endpoint contributor; client thường nhận refresh URL qua table config khi yêu cầu vending.
- Page token hiện không ký. Client phải coi token opaque và server/operator không nên coi nội dung token là nguồn authorization; authorization vẫn phải chạy lại ở request sau.

Các điểm này là quan sát source tại commit đã nêu, không phải tuyên bố về mọi deployment Polaris.

## 21. Cách kiểm chứng triển khai

1. Chốt tag Polaris cần đánh giá, ví dụ 1.7.0 thay vì `main`.
2. Lấy `/api/catalog/v1/config?warehouse=...` và lưu chính xác `endpoints`, `overrides`, idempotency lifetime.
3. Chạy Apache Iceberg REST Compatibility Kit (RCK) với server đó. Hướng dẫn chính thức: [`open-api/README.md`](https://github.com/apache/iceberg/blob/main/open-api/README.md#rest-compatibility-kit).
4. Test riêng các đường Polaris-specific:
   - realm thiếu/sai;
   - role scope chưa được grant;
   - vended read-only và read-write credentials;
   - custom/staged location;
   - concurrent single-table commit;
   - atomic multi-table failure + metadata cleanup;
   - pagination feature on/off;
   - ETag `refs` so với `all`;
   - internal so với federated catalog.
5. Quan sát cả metastore pointer và object-store files; chỉ nhìn HTTP 2xx không đủ để kiểm chứng cleanup/atomicity.

## 22. Vị trí của chương này trong bản đồ nghiên cứu

```text
API / Protocol Layer
└── Iceberg REST API  ← chương này
    ├── Wire spec và endpoint capability
    ├── Generated JAX-RS API
    ├── IcebergCatalogAdapter
    ├── giao Security: realm/auth/RBAC
    ├── giao Catalog Service: IcebergCatalogHandler
    ├── giao Metadata: resolver + metastore CAS
    ├── giao Persistence: atomic entity update
    ├── giao Storage: FileIO + credential vending
    └── giao Supporting: events/metrics/cleanup
```

Các phần chỉ được nhắc ở mức giao diện và nên có chương riêng sau này: Polaris Management API; toàn bộ OAuth/OIDC internals; RBAC/grant inheritance; Generic Table/Policy Handler; entity cache; chi tiết JDBC/NoSQL schema; cloud provider integration; background tasks.

## 23. Nguồn chính thức chính

- [Apache Iceberg REST Catalog Spec](https://iceberg.apache.org/rest-catalog-spec/)
- [Apache Iceberg OpenAPI `main`](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml)
- [Apache Iceberg OpenAPI 1.11.0](https://github.com/apache/iceberg/blob/apache-iceberg-1.11.0/open-api/rest-catalog-open-api.yaml)
- [Apache Iceberg REST Compatibility Kit](https://github.com/apache/iceberg/blob/main/open-api/README.md#rest-compatibility-kit)
- [Apache Iceberg REST catalog properties](https://iceberg.apache.org/docs/latest/catalog-properties/)
- [Apache Polaris catalog OpenAPI](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/spec/polaris-catalog-service.yaml)
- [Apache Polaris source — Iceberg catalog package](https://github.com/apache/polaris/tree/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg)
- [Apache Polaris 1.7.0 documentation](https://polaris.apache.org/releases/1.7.0/)
- [Polaris RBAC documentation](https://polaris.apache.org/releases/1.7.0/managing-security/access-control/)
- [Polaris vended credentials documentation](https://polaris.apache.org/releases/1.7.0/vended-credentials/)
- [Polaris Iceberg REST federation documentation](https://polaris.apache.org/releases/1.7.0/federation/iceberg-rest-federation/)

## 24. Phương pháp

Nghiên cứu dùng tài liệu và repository chính thức của Apache. Đặc tả living `main` được so sánh trực tiếp với bản Iceberg 1.11.0 copy trong Polaris; source Polaris được checkout tại commit cố định và truy vết từ OpenAPI generator qua adapter, handler, local catalog, table operations, metastore, auth/RBAC, storage credential và error mapper. Các nhận định “chưa hỗ trợ” chỉ được đưa ra khi OpenAPI Polaris loại endpoint hoặc source chủ động reject code path.

## Đối chiếu cuối báo cáo — Bảy câu hỏi cốt lõi

Phần này trả lời về **Polaris qua Iceberg REST API**, đồng thời chỉ rõ phần việc thuộc API/Protocol Layer. Giữ nguyên các mốc phiên bản của chương; giao thức REST tự nó không phải một catalog implementation hay một persistence backend.

### 1. Nó quản lý loại metadata nào?

API biểu diễn namespace, table/view metadata, properties, requirements và updates theo Iceberg REST contract. Polaris bên dưới quản lý entity, hierarchy, metadata references và thông tin quản trị. Dữ liệu schema/spec/snapshot thuộc mô hình Iceberg; API truyền chúng dưới dạng request/response, không biến chúng thành rows dữ liệu nghiệp vụ lưu ở server. Xem mục 3, 6 và 12. [Iceberg REST specification](https://iceberg.apache.org/rest-catalog-spec/)

### 2. Metadata persistence nằm ở đâu?

**API layer không có kho metadata bền vững riêng.** Entity và điểm tham chiếu của catalog local được lưu qua Polaris metastore/persistence backend đã cấu hình; PostgreSQL/JDBC là một đường triển khai được tài liệu mô tả. Metadata JSON, manifests và data/delete files thuộc storage của bảng. Response/cache trong client không thay thế hai miền persistence này. Với federation, trạng thái bảng có thể thuộc catalog phía sau. [Polaris metastore configuration](https://polaris.apache.org/releases/1.7.0/metastores/)

### 3. Engine resolve một table như thế nào?

Engine bootstrap bằng catalog URI và authentication, lấy config để xác định warehouse/prefix/capabilities rồi gọi load-table bằng namespace/table. Polaris resolve realm, identity và resource path, kiểm tra quyền rồi chọn local hoặc federated catalog. Response trả table metadata cùng config/credential nếu được yêu cầu và cho phép. Engine dùng metadata này để planning, không gọi trực tiếp database của Polaris. Xem mục 4 và 9.

### 4. Read path và write/commit path như thế nào?

**Read:** load-table REST → resolve/authorize → load metadata → response → engine đọc manifests và data/delete files trên storage.

**Write:** engine chuẩn bị data/delete files và metadata phụ trợ cần thiết, gửi requirements/updates; Polaris kiểm tra điều kiện, áp dụng cập nhật bằng Iceberg library, ghi metadata JSON mới và yêu cầu công bố reference có điều kiện. HTTP thành công phản ánh commit đã được catalog chấp nhận, không chỉ việc upload file xong. Conflict và kết quả commit không rõ cần xử lý riêng; số round trip thay đổi theo cache/operation. Xem mục 10–11.

### 5. Table state/version được quản lý bởi catalog hay table format?

Iceberg quy định schema/spec, snapshot, metadata evolution và cách diễn giải files. Polaris bảo vệ bước công bố metadata hiện hành cùng trạng thái entity của catalog. REST chuẩn hóa giao tiếp giữa client và server. Vì vậy, **snapshot ID, entity version và HTTP ETag không phải cùng một loại version**.

Đổi properties/schema có thể tạo metadata mới mà không tạo snapshot dữ liệu mới. Việc đặc tả có endpoint multi-table transaction không tự chứng minh mọi backend triển khai được atomic multi-table commit; phải kiểm tra capability và đường thực thi nêu ở mục 11. [Iceberg specification](https://iceberg.apache.org/spec/)

### 6. Security và storage credential được xử lý ở đâu?

API nhận token và access-delegation request. Security xác thực principal/active roles và đánh giá operation; handler kiểm tra resource/location trước khi Storage Integration cấp credential theo phạm vi. Quyền load metadata không tự cho phép vending read/write credentials. Client dùng credential được cấp hoặc credential riêng hợp lệ để đọc storage; cloud IAM/KMS vẫn thực thi quyền.

Trong source snapshot của chương, remote signing bị chủ động từ chối; không suy ra Polaris hỗ trợ chỉ vì REST specification có khái niệm đó. Xem mục 13–14. [Vended credentials](https://polaris.apache.org/releases/1.7.0/vended-credentials/)

### 7. Điểm khác biệt cốt lõi của catalog này là gì?

Ở góc độ chương này, Polaris cung cấp **giao diện Iceberg REST để nhiều engine dùng chung nghiệp vụ catalog, authorization và credential delegation phía server**. Engine giảm phụ thuộc vào API/backend riêng của metastore. Tuy nhiên, REST compatibility không đồng nghĩa mọi implementation có cùng persistence, security, federation hoặc transaction guarantees; đó là các đặc tính phải kiểm chứng bên dưới API.
