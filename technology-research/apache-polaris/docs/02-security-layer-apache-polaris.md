# Chương 2 — Security Layer trong kiến trúc Apache Polaris

*Ngày nghiên cứu: 05-09-2026 · Phạm vi chính xác: `Security Layer → Authentication + Authorization/RBAC`. Tài liệu chính thức lấy mốc release ổn định 1.7.0; phần đọc mã nguồn lấy `main` commit `9da600803a540ae168580053c952f8ac6c947986` ngày 01-09-2026.*

## 1. Kết luận kiến trúc

Security Layer của Polaris không phải một middleware duy nhất đứng trước controller. Nó là một chuỗi kiểm soát gồm bốn câu hỏi nối tiếp nhau:

1. Request thuộc **realm** nào?
2. Bearer token có hợp lệ và ánh xạ tới **principal** nào?
3. Những **principal role** nào thực sự đang được kích hoạt cho request này?
4. Principal, qua các role đang hoạt động, có đủ privilege trên đúng resource path để thực hiện operation không?

```text
HTTP request
  │
  ▼
RealmContextFilter
  └─ chọn realm; realm quyết định security domain và metastore session
  │
  ▼
Quarkus authentication mechanism
  ├─ INTERNAL: Polaris JWT → TokenBroker.verify
  ├─ EXTERNAL: OIDC JWT → Quarkus OIDC verify
  └─ MIXED: thử internal trước, thất bại thì để OIDC thử
  │
  ▼
PolarisCredential
  └─ principalId/name + các principal role được yêu cầu
  │
  ▼
DefaultAuthenticator
  ├─ principal có thật trong realm hiện tại không?
  └─ các role yêu cầu có thật sự được grant cho principal không?
  │
  ▼
PolarisPrincipal
  └─ principal đã xác thực + tập principal role đang active
  │
  ▼
Handler dựng AuthorizationRequest
  ├─ operation
  ├─ một hoặc nhiều intent
  └─ target / secondary resource path
  │
  ▼
PolarisAuthorizer
  ├─ internal → RBAC
  ├─ opa      → external PDP
  └─ ranger   → extension trong source main
  │
  ▼
ALLOW → handler mới được đọc/sửa metadata hoặc yêu cầu credential vending
DENY  → 403; authentication hỏng → 401
```

Điểm cốt lõi là: **token hợp lệ không đồng nghĩa với request được phép**. Chữ ký token chỉ chứng minh credential được issuer tin cậy cấp và chưa hết hạn. Polaris vẫn tra trạng thái principal/role hiện tại trong metastore, rồi mới đánh giá quyền trên từng operation. Đây là cách mã nguồn hiện thực nguyên tắc “authenticated ≠ authorized” trong [threat model chính thức](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/SECURITY-THREAT-MODEL.md#trust-boundaries).

## 2. Security Layer nằm ở đâu trong sơ đồ nghiên cứu?

Trong kiến trúc của bạn, vị trí đúng là:

```text
API / Protocol Layer
  ├─ Iceberg REST API
  ├─ Polaris Management API
  └─ OAuth API
          │
          ▼
Security Layer                       ← chương này
  ├─ Realm-bound request context
  ├─ Authentication
  └─ Authorization / RBAC
          │
          ▼
Catalog Service Layer
          │
          ▼
Metadata Management / Persistence / Storage
```

Security là **lớp cắt ngang** chứ không chỉ là một hộp đứng độc lập:

- OAuth API là đầu vào để phát token internal, nhưng logic ký/kiểm tra token thuộc Authentication.
- Iceberg REST và Management API là hai mặt API khác nhau, nhưng cùng dùng `PolarisPrincipal` và `PolarisAuthorizer`.
- Authorization cần Metadata/Persistence để resolve entity, role và grant. Điều đó không biến Security thành Persistence; metastore chỉ cung cấp trạng thái mà Security dùng để quyết định.
- `TABLE_READ_DATA`/`TABLE_WRITE_DATA` là quyết định bảo mật dẫn tới credential vending. Việc tạo credential cloud nằm ở Storage Integration, nhưng điều kiện cho phép nằm ở Security.

Vì vậy chương này đi sâu đến **điểm quyết định bảo mật**, không đi xuống thuật toán commit Iceberg, cấu trúc bảng JDBC hay cách AWS STS tạo session token.

## 3. Mốc phiên bản và phương pháp đọc

### 3.1 Hai mốc phải tách biệt

- **Polaris 1.7.0** là release ổn định mới nhất tại thời điểm nghiên cứu, phát hành 02-08-2026 theo [trang tải chính thức](https://polaris.apache.org/downloads/). Các tên cấu hình, ba authentication mode, RBAC công khai và OPA trong tài liệu này ưu tiên theo docs 1.7.0.
- Source được đọc ở commit [`9da6008`](https://github.com/apache/polaris/commit/9da600803a540ae168580053c952f8ac6c947986), mới hơn release 1.7.0 khoảng một tháng. `main` đã có SPI authorization theo `AuthorizationRequest`/`AuthorizationIntent`, Ranger extension và tập fine-grained table-update privileges. Những phần này được ghi rõ là **source main**, không mặc định coi là contract của binary 1.7.0.

### 3.2 Ba mức bằng chứng

Tài liệu dùng ba nhãn ngầm:

- **Public contract**: hành vi được docs 1.7.0 công bố.
- **Source fact**: hành vi đọc trực tiếp từ source tại commit cố định.
- **Inference**: hệ quả suy ra từ nhiều đoạn mã; sẽ được nói rõ là nhận định, không phải cam kết API.

Nguồn chính gồm [RBAC 1.7.0](https://polaris.apache.org/releases/1.7.0/managing-security/access-control/), [Identity Providers 1.7.0](https://polaris.apache.org/releases/1.7.0/managing-security/external-idp/), [Realm 1.7.0](https://polaris.apache.org/releases/1.7.0/realm/), [External PDP](https://polaris.apache.org/releases/1.7.0/managing-security/external-pdp/), [OPA](https://polaris.apache.org/releases/1.7.0/managing-security/external-pdp/opa/), [configuration reference](https://polaris.apache.org/releases/1.7.0/configuration/configuration-reference/) và source commit nêu trên.

## 4. Mô hình khái niệm: đừng trộn bốn thứ với nhau

| Khái niệm | Câu hỏi nó trả lời | Artifact chính |
|---|---|---|
| Realm resolution | Request thuộc miền cô lập nào? | `RealmContext` |
| Authentication | Caller là ai và role nào được active? | `PolarisPrincipal` |
| Authorization | Caller được phép làm operation nào trên resource nào? | `AuthorizationDecision` |
| Enforcement | Nếu allow/deny thì handler phải làm gì? | tiếp tục hoặc ném lỗi |

Một ví dụ:

```text
Realm          = production
Principal      = spark_etl
Active roles   = {data_engineer}
Catalog role   = sales_writer trong catalog sales
Operation      = LOAD_TABLE_WITH_WRITE_DELEGATION
Target         = sales.finance.orders
Required priv  = TABLE_WRITE_DATA
Decision       = allow / deny
```

OIDC tenant không phải realm. OIDC tenant mô tả **issuer và cách kiểm tra token**; realm mô tả **partition nội bộ của Polaris**. Nhiều realm có thể dùng chung một OIDC tenant, nhưng mỗi realm chỉ gắn với một tenant OIDC trong cấu hình mặc định. [Docs 1.7.0 giải thích ranh giới này](https://polaris.apache.org/releases/1.7.0/managing-security/external-idp/#oidc-tenant-configuration).

## 5. Trust model và security invariants

Threat model trong repo nêu các giả định nền tảng sau:

- caller trên mạng chưa được tin cậy cho đến khi authentication thành công;
- principal đã xác thực vẫn không mặc nhiên được truy cập resource;
- mọi identifier do request cung cấp — catalog, namespace, table, role, policy, principal name — đều là dữ liệu không tin cậy;
- claim của IdP chỉ đáng tin sau khi token được xác minh theo mechanism đã cấu hình;
- authorization phải xảy ra trước khi trả metadata được bảo vệ hoặc mutate trạng thái;
- grant/role management phải chặn các đường leo thang gián tiếp như self-grant hoặc role nesting;
- credential vending chỉ được xảy ra sau kiểm tra location, authorization và scope;
- lỗi không được làm lộ secret hoặc metadata mà caller không có quyền biết;
- management plane và catalog data plane có thể cần các kiểm tra khác nhau.

Nguồn: [Security Threat Model — Trust Boundaries và Security Invariants](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/SECURITY-THREAT-MODEL.md#security-invariants).

Từ đó có thể mô tả điều kiện tối thiểu của một request bảo vệ:

```text
ACCEPT(request)
  = validRealm(request)
  ∧ validCredential(request)
  ∧ managedPrincipalExists(request.realm, subject)
  ∧ requestedRoles ⊆ currentlyGrantedRoles
  ∧ authorizerAllows(operation, subject, resource)
```

Nếu một mệnh đề sai, handler không được thực hiện side effect bảo vệ.

## 6. Bước 0 — Realm resolution

### 6.1 Vì sao realm đứng trước authentication?

Principal và grant không tồn tại trong một không gian toàn cục vô danh. Polaris cần biết realm trước để chọn đúng:

- metastore session;
- authentication configuration;
- token broker/key;
- OIDC tenant mapping;
- feature configuration và tập entity/grant.

Docs mô tả realm là partition logic cho multitenancy: resource, policy và credential của realm này không được ảnh hưởng realm khác. Với JDBC, realm ID tham gia khóa lưu trữ; vì vậy cùng tên `alice` ở hai realm là hai identity context khác nhau. [Realm 1.7.0](https://polaris.apache.org/releases/1.7.0/realm/).

### 6.2 Logic trong source

[`RealmContextFilter`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/context/RealmContextFilter.java) là pre-matching request filter:

1. đưa URL, method, path và hàm đọc header cho `RealmContextResolver`;
2. ghi kết quả vào `RealmContextHolder`, request property và Vert.x context-local;
3. các producer request-scoped sau đó dùng context này để lấy `CallContext`, `RealmConfig` và persistence session.

[`DefaultRealmContextResolver`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/context/DefaultRealmContextResolver.java) áp dụng quy tắc:

```text
nếu header có mặt:
    realm phải thuộc tập realms cấu hình
nếu header vắng:
    require-header = true  → reject
    require-header = false → dùng realm đầu tiên/default
```

Realm thiếu hoặc không hợp lệ được filter chuyển thành HTTP `404`, Iceberg `ErrorResponse` type `MissingOrInvalidRealm`. Đây là một quyết định tránh cung cấp chi tiết phân biệt “realm thiếu” và “realm không tồn tại”, không phải lỗi authentication `401`.

Các khóa cấu hình liên quan là `polaris.realm-context.realms`, `header-name`, `require-header`, `type`; [configuration reference](https://polaris.apache.org/releases/1.7.0/configuration/configuration-reference/#polarisrealm-context) ghi chú việc bắt buộc header thực sự được enforce trong production setup.

## 7. Authentication: kiến trúc chung

Authentication của Polaris có hai tầng:

```text
Tầng A — kiểm tra credential kỹ thuật
  internal: verify JWT signature/issuer/active/expiry
  external: Quarkus OIDC kiểm tra issuer/signature/token

Tầng B — nối credential vào identity model của Polaris
  resolve principal trong realm
  kiểm tra role yêu cầu thật sự được grant
  tạo PolarisPrincipal
```

Tầng B đặc biệt quan trọng. Một JWT OIDC hoàn toàn hợp lệ nhưng claim trỏ đến principal không tồn tại trong Polaris vẫn thất bại. Tương tự, token mang `PRINCIPAL_ROLE:admin` nhưng principal không được grant role `admin` cũng thất bại.

### 7.1 Ba authentication mode

| Mode | Ai phát token? | Cơ chế nhận request | Internal token endpoint |
|---|---|---|---|
| `internal` | Polaris | `TokenBroker.verify` | bật |
| `external` | IdP OIDC | Quarkus OIDC | tắt, trả `501` |
| `mixed` | cả hai | thử internal trước, rồi OIDC | bật |

`internal` là mặc định. Cấu hình có thể đặt global hoặc override theo realm, ví dụ `polaris.authentication.<realm>.type`. Nguồn: [Identity Providers 1.7.0](https://polaris.apache.org/releases/1.7.0/managing-security/external-idp/#authentication-types) và [configuration reference](https://polaris.apache.org/releases/1.7.0/configuration/configuration-reference/#polarisauthentication).

## 8. Internal authentication

### 8.1 Luồng `client_credentials`

Endpoint token là:

```http
POST /api/catalog/v1/oauth/tokens
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&
client_id=spark_etl&
client_secret=...&
scope=PRINCIPAL_ROLE:data_engineer
```

Luồng source:

```text
DefaultOAuth2ApiService.getToken
  → kiểm tra grant_type và requested_token_type
  → lấy client_id/client_secret từ form hoặc HTTP Basic
  → JWTBroker.generateFromClientSecrets
      → TokenRequestValidator
      → loadPrincipalSecrets(clientId)
      → matchesSecret(clientSecret)
      → findPrincipalById
      → generateTokenString
  → OAuthTokenResponse
```

[`DefaultOAuth2ApiService`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/internal/service/DefaultOAuth2ApiService.java) hỗ trợ hai đường: client credentials và token exchange. Nếu có `Authorization: Basic ...` mà form không có secret, service tách chuỗi `clientId:clientSecret` và xử lý như client credentials.

### 8.2 Scope không phải privilege

`scope` internal có dạng:

```text
PRINCIPAL_ROLE:<role-1> PRINCIPAL_ROLE:<role-2>
```

Nó chọn **principal roles muốn kích hoạt trong session**, không trực tiếp chứa `TABLE_READ_DATA` hay privilege khác. [`TokenRequestValidator`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/internal/broker/TokenRequestValidator.java) yêu cầu scope cho client-credentials dù Iceberg/OAuth contract tổng quát có thể coi nó optional; mỗi token phải có prefix đúng và tên role không rỗng.

Đây là cơ chế least privilege theo session:

```text
Principal có roles = {data_reader, data_writer, service_admin}
Token chỉ yêu cầu = {data_reader}
⇒ request không được dùng data_writer hoặc service_admin qua token đó
```

Docs cung cấp cú pháp và ví dụ đầy đủ tại [Internal Role Mapping](https://polaris.apache.org/releases/1.7.0/managing-security/external-idp/#role-mapping).

### 8.3 JWT mà Polaris tự phát hành

[`JWTBroker`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/internal/broker/JWTBroker.java) tạo JWT có các trường quan trọng:

| Claim | Ý nghĩa |
|---|---|
| `iss=polaris` | issuer nội bộ |
| `sub` | principal name |
| `principalId` | ID entity principal |
| `client_id` | client ID dùng phát token |
| `scope` | principal roles yêu cầu |
| `iat`, `exp` | thời điểm phát và hết hạn |
| `jti` | token ID ngẫu nhiên |
| `active=true` | claim bắt buộc bởi verifier |

Verifier bắt buộc đúng algorithm đã cấu hình, issuer `polaris`, `active=true`; thư viện JWT cũng kiểm tra expiration. Token lifetime tối đa mặc định `PT1H`. Polaris hỗ trợ:

- `rsa-key-pair`: khuyến nghị cho production;
- `symmetric-key`: phù hợp single-node hoặc test.

Trong multi-replica, các pod phải dùng chung signing keys; nếu mỗi pod tự sinh key khác nhau thì token do pod A phát sẽ không được pod B xác minh. Đây là cảnh báo chính thức trong [Helm authentication guide](https://polaris.apache.org/releases/1.7.0/helm-chart/authentication/#internal-authentication).

### 8.4 Token exchange

`JWTBroker.generateFromToken` thực hiện:

1. chỉ chấp nhận subject token và requested token type là access token;
2. verify subject JWT;
3. kiểm tra principal ID vẫn tồn tại;
4. nếu request xin scope mới, scope mới phải là tập con của scope cũ;
5. ngoại lệ: token cũ có pseudo-role `PRINCIPAL_ROLE:ALL` có thể thu hẹp về tập role cụ thể;
6. phát JWT mới với thời hạn tối đa cấu hình.

Không thể dùng token exchange để tự mở rộng từ `data_reader` sang `service_admin`.

### 8.5 Client secret được kiểm tra ra sao?

Source model [`PolarisPrincipalSecrets`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/entity/PolarisPrincipalSecrets.java) giữ hash SHA-256 của `secret:salt`, có main và secondary hash để hỗ trợ rotation. Persistence JDBC có các cột hash thay vì lưu plaintext secret làm credential kiểm tra. Secret plaintext chỉ được trả ở thời điểm tạo/rotate/reset thích hợp; vận hành phải xem output đó là bí mật.

### 8.6 Nhận JWT internal ở request sau

[`InternalAuthenticationMechanism`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/internal/InternalAuthenticationMechanism.java):

1. bỏ qua hoàn toàn khi mode là `external`;
2. đọc `Authorization: Bearer <token>`;
3. gọi `TokenBroker.verify`;
4. nếu hợp lệ, tạo internal security identity chứa `PolarisCredential`;
5. nếu không hợp lệ trong `internal`, dừng với authentication failure;
6. nếu không hợp lệ trong `mixed`, trả `null` để Quarkus OIDC có cơ hội nhận token.

Priority của mechanism này cao hơn OIDC, vì mixed mode phải thử internal trước.

## 9. External authentication qua OIDC

### 9.1 Phân chia trách nhiệm

```text
External IdP
  └─ phát access token

Quarkus OIDC
  ├─ chọn OIDC tenant
  ├─ kiểm tra signature/issuer/expiry theo cấu hình IdP
  └─ tạo SecurityIdentity + JsonWebToken

Polaris OIDC augmentor
  ├─ map claim → principalId / principalName
  └─ map IdP roles → PRINCIPAL_ROLE:...

DefaultAuthenticator
  ├─ đối chiếu principal với metastore của realm
  └─ đối chiếu role với grant hiện tại
```

Polaris không tin trực tiếp chuỗi username hoặc role trong JWT. Quarkus xác minh token trước; sau đó [`OidcPolarisCredentialAugmentor`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/external/OidcPolarisCredentialAugmentor.java) mới tạo `PolarisCredential`.

### 9.2 Principal mapping

Có thể map theo ID, name hoặc cả hai:

```properties
polaris.oidc.principal-mapper.id-claim-path=polaris/principal_id
polaris.oidc.principal-mapper.name-claim-path=polaris/principal_name
```

Nếu có principal ID hợp lệ, `DefaultAuthenticator` ưu tiên lookup theo ID; nếu không thì theo name. Default principal mapper chỉ làm việc với JWT. IdP phát opaque token cần custom mapper. [OIDC Principal Mapping 1.7.0](https://polaris.apache.org/releases/1.7.0/managing-security/external-idp/#principal-mapping).

### 9.3 Role mapping hai pha

1. Quarkus đọc role claim theo `quarkus.oidc.roles.*`.
2. Polaris filter và regex-transform role thành dạng `PRINCIPAL_ROLE:<name>`.

Ví dụ:

```properties
quarkus.oidc.roles.role-claim-path=polaris/roles
polaris.oidc.principal-roles-mapper.filter=^(?!profile$|email$).*
polaris.oidc.principal-roles-mapper.mappings[0].regex=^.*$
polaris.oidc.principal-roles-mapper.mappings[0].replacement=PRINCIPAL_ROLE:$0
```

Mapping chỉ là chuyển namespace/tên; nó không tự cấp role. Comment trong source nói rõ augmentor chưa đổi active identity roles ở bước này, vì `AuthenticatingAugmentor` sẽ validate chúng về sau. Nguồn: [Role Mapping 1.7.0](https://polaris.apache.org/releases/1.7.0/managing-security/external-idp/#role-mapping-1).

### 9.4 Giới hạn managed-principal

`DefaultAuthenticator` tại commit nghiên cứu ghi rõ chưa hỗ trợ federated principal không được Polaris quản lý. Do đó external authentication mặc định vẫn cần một `PrincipalEntity` tương ứng trong Polaris. OIDC là **nguồn chứng minh identity**, không tự thay thế identity/role graph nội bộ.

## 10. Bước hợp nhất — `DefaultAuthenticator`

Sau internal hoặc OIDC, [`AuthenticatingAugmentor`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/AuthenticatingAugmentor.java) gọi `Authenticator` và thay principal của Quarkus identity bằng `PolarisPrincipal`.

[`DefaultAuthenticator`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/DefaultAuthenticator.java) chạy logic:

```text
input PolarisCredential
  │
  ├─ principalId > 0 ? findPrincipalById : findPrincipalByName
  │    └─ không thấy / sai type → authentication failure
  │
  ├─ đọc requested roles
  │    ├─ có PRINCIPAL_ROLE:ALL → yêu cầu mọi role đã grant
  │    └─ không → bỏ prefix PRINCIPAL_ROLE:
  │
  ├─ loadGrantsToGrantee(principal)
  ├─ chỉ lấy securable entity có type PRINCIPAL_ROLE
  ├─ giao với requested roles
  │
  └─ nếu role cụ thể nào được yêu cầu nhưng không có grant → authentication failure

output PolarisPrincipal(name, attributes, activeRoleNames)
```

`PolarisPrincipal` giữ:

- `PrincipalEntity` đã resolve;
- tập role active;
- cờ có yêu cầu `ALL` hay không;
- raw JWT khi đầu vào là OIDC `JsonWebToken`.

Không merge tùy tiện attributes từ Quarkus identity vào principal attributes. Điều này giữ ranh giới rõ giữa dữ liệu platform identity và dữ liệu Polaris đã xác nhận.

### 10.1 Ý nghĩa bảo mật của active roles

Gọi:

```text
GrantedRoles(P) = các principal role hiện đang được grant cho P
RequestedRoles(T) = role có trong token/claim sau mapping
```

thì:

```text
ActiveRoles(P,T) = GrantedRoles(P) ∩ RequestedRoles(T)
```

với điều kiện mọi requested role cụ thể phải thuộc `GrantedRoles`; nếu không, cả authentication thất bại. Với `PRINCIPAL_ROLE:ALL`, active roles bằng toàn bộ granted roles.

Role không có prefix `PRINCIPAL_ROLE:` bị bỏ qua và được ghi warning. Vì thế credential có thể xác thực thành công với tập active role rỗng; khi đó các protected operation thường sẽ bị authorizer từ chối vì không có activated grantee thỏa privilege.

Hệ quả quan trọng: revoke một principal-role grant có hiệu lực ở request mới dù token cũ vẫn mang tên role, vì authenticator đọc grant hiện tại chứ không tin claim đơn độc.

### 10.2 Metastore lỗi không được giả thành “sai mật khẩu”

Source phân biệt lỗi dependency và credential: lỗi khi resolve principal/grant được bọc thành service unavailable; principal/role không tồn tại trở thành authentication failure. Về vận hành, điều này giúp tránh chẩn đoán sai outage metastore thành lượng lớn login failure.

## 11. Credential rotation, reset và hiệu lực token

Polaris phân biệt:

- **rotate credentials**: principal tự đổi credential; source dùng main/secondary secret hash để hỗ trợ chuyển tiếp;
- **reset credentials**: thao tác quản trị mạnh hơn; trong internal authorizer hiện chỉ root principal được thực hiện;
- **rotation-required state**: khi feature enforcement bật và principal bị đánh dấu phải rotate, mọi operation trừ `ROTATE_CREDENTIALS` bị từ chối bởi [`AuthorizationPreConditions`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/AuthorizationPreConditions.java).

Management handler có một self-service rule: principal đã xác thực được rotate **credential của chính mình** sau khi target principal được resolve và so tên, không cần `PRINCIPAL_ROTATE_CREDENTIALS`. Rotate credential của principal khác vẫn đi qua authorizer. Reset là luồng quản trị riêng.

Một chi tiết source cần hiểu chính xác:

- `JWTBroker.verify` xác minh chữ ký, issuer, `active=true` và expiry, nhưng không thấy một token deny-list/JTI revocation lookup trong class này;
- `DefaultAuthenticator` vẫn kiểm tra principal tồn tại và role grant ở mỗi request;
- vì vậy xóa principal hoặc revoke role chặn request tiếp theo, nhưng **chỉ rotate/reset client secret không tự nó chứng minh rằng JWT đã phát bị thu hồi ngay**. Theo logic được đọc, access token cũ có thể còn dùng tới `exp` nếu principal/role/state vẫn hợp lệ.

Đây là **inference từ source commit**, không phải tuyên bố contract cho mọi deployment/custom broker. Biện pháp vận hành là dùng lifetime ngắn, bảo vệ signing key, và nếu cần revocation tức thời thì phải xác nhận broker/IdP triển khai có cơ chế tương ứng.

## 12. Authorization SPI: từ business operation đến quyết định allow/deny

Authentication kết thúc ở `PolarisPrincipal`. Authorization bắt đầu khi handler mô tả **caller muốn làm gì với resource nào**.

### 12.1 Năm artifact quan trọng

| Artifact | Vai trò |
|---|---|
| `PolarisAuthorizableOperation` | tên hành động trung lập với policy, ví dụ `LOAD_TABLE`, `RENAME_TABLE` |
| `PolarisSecurable` | resource path có thứ tự, ví dụ catalog → namespace → table |
| `AuthorizationIntent` | một yêu cầu quyền với hình dạng target/secondary cụ thể |
| `AuthorizationRequest` | principal + một hoặc nhiều intent |
| `AuthorizationState` | state đã resolve cho authorizer trong request |

Source: [`PolarisAuthorizer`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/PolarisAuthorizer.java), [`AuthorizationRequest`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/AuthorizationRequest.java), [`AuthorizationIntent`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/AuthorizationIntent.java), [`PolarisSecurable`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/PolarisSecurable.java).

### 12.2 Các hình dạng intent

`AuthorizationIntent` là sealed interface với các loại:

- `TargetlessAuthorizationIntent`: operation không có resource công khai rõ ràng;
- `SingleTargetAuthorizationIntent`: một target;
- `RenameAuthorizationIntent`: source là target, destination là secondary;
- `PolicyAttachmentAuthorizationIntent`: policy và entity được gắn;
- `RoleAssignmentAuthorizationIntent`: role và assignee;
- `PrivilegeGrantAuthorizationIntent`: securable nhận privilege và grantee;
- `RootPrivilegeGrantAuthorizationIntent`: grant ở root/service scope và grantee.

Việc biểu diễn cả target lẫn secondary ngăn một lỗi tư duy phổ biến: chỉ kiểm tra quyền trên object nguồn mà quên object đích hoặc bên nhận quyền.

Ví dụ rename table:

```text
intent.operation = RENAME_TABLE
intent.from      = catalogA.ns.old_name
intent.to        = catalogA.ns.new_name

required on from = TABLE_DROP
required on to   = TABLE_LIST + TABLE_CREATE
```

### 12.3 Nhiều intent là phép AND

Contract của `PolarisAuthorizer` nói rõ: nếu một request có nhiều intents, authorizer phải AND-combine toàn bộ và có thể short-circuit ở deny đầu tiên.

```text
ALLOW(request) = ALLOW(intent₁) ∧ ALLOW(intent₂) ∧ ... ∧ ALLOW(intentₙ)
```

Điều này cần cho transaction/multi-resource operations: không thể “được phép một nửa” rồi vẫn thực hiện side effect nguyên tử.

### 12.4 Chọn implementation

[`ServiceProducers`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/config/ServiceProducers.java) đọc `polaris.authorization.type`, chọn `PolarisAuthorizerFactory` có CDI identifier tương ứng, rồi tạo authorizer request-scoped:

```text
polaris.authorization.type=internal → PolarisAuthorizerImpl
polaris.authorization.type=opa      → OpaPolarisAuthorizer
polaris.authorization.type=ranger   → Ranger extension nếu distribution chứa nó
```

Default công khai của 1.7.0 là `internal`. [External PDP docs](https://polaris.apache.org/releases/1.7.0/managing-security/external-pdp/#configuration).

## 13. Internal RBAC: mô hình dữ liệu quyền

### 13.1 Đồ thị cấp quyền

RBAC công khai của Polaris có bốn tầng:

```text
Principal
   │ PRINCIPAL_ROLE_USAGE
   ▼
Principal Role
   │ CATALOG_ROLE_USAGE
   ▼
Catalog Role                    (thuộc đúng một catalog)
   │ privilege grant
   ▼
Securable
   ├─ catalog
   ├─ namespace
   ├─ Iceberg table / generic table
   ├─ view
   └─ policy
```

Quan hệ principal ↔ principal role là many-to-many. Quan hệ principal role ↔ catalog role cũng là many-to-many, nhưng catalog role thuộc một catalog cụ thể. [RBAC 1.7.0](https://polaris.apache.org/releases/1.7.0/managing-security/access-control/#rbac-model).

Phân vai:

- **Principal**: identity có thể đăng nhập.
- **Principal role**: nhóm identity theo chức năng tổ chức, ví dụ `data_engineer`.
- **Catalog role**: bundle quyền trong một catalog, ví dụ `sales_reader`.
- **Privilege**: capability nguyên tử hoặc super-privilege trên securable.

Không cấp table privilege trực tiếp cho principal role theo mô hình công khai. Privilege cấp cho catalog role; catalog role cấp cho principal role; principal role cấp cho principal.

### 13.2 Grant record lưu gì?

Một `PolarisGrantRecord` về bản chất biểu diễn cạnh:

```text
(securableCatalogId, securableId,
 granteeCatalogId,  granteeId,
 privilegeCode)
```

Ví dụ:

```text
(sales, namespace finance,
 sales, catalog-role sales_reader,
 TABLE_READ_DATA)
```

Grant record dùng ID thay vì chỉ dùng name, tránh quyền vô tình “chuyển” sang entity mới có cùng tên sau rename/drop/recreate. Entity và grant còn có version để hỗ trợ cache coherence.

## 14. Entity resolution cho authorization

Authorization không thể so chuỗi `sales.finance.orders` một cách ngây thơ. Nó cần resolve:

1. caller principal;
2. principal roles đang active;
3. reference catalog;
4. catalog roles được cấp từ các principal role active trong đúng catalog đó;
5. target và secondary paths;
6. grant records trên từng node của path.

[`Resolver`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/persistence/resolver/Resolver.java) thực hiện theo thứ tự đó. Catalog role chỉ được activate nếu grant `CATALOG_ROLE_USAGE` có `securableCatalogId` bằng catalog hiện tại. Do vậy catalog role `reader` của catalog `sales` không tự có tác dụng trong catalog `hr` dù trùng tên.

### 14.1 Resource path

`PolarisSecurable` yêu cầu path từ parent xa nhất tới leaf:

```text
[CATALOG sales,
 NAMESPACE finance,
 TABLE_LIKE orders]
```

Nó validate quan hệ cha-con theo `PolarisEntityType`; `ROOT` không được đưa vào path công khai và top-level entity không được có parent. Internal authorizer có thể thêm root container khi operation semantics yêu cầu service-level privilege.

### 14.2 Cache không được quyết định quyền dựa trên state tùy tiện cũ

Resolver có thể đọc entity từ cache để nhanh hơn, nhưng cuối resolve pass nó bulk-validate `entityVersion` và `grantRecordsVersion` với backend. Nếu principal/principal-role grant thay đổi, hoặc entity bị drop/rename/re-parent, resolver buộc chạy pass khác/refetch. Comment source gọi mục tiêu này là happens-before semantics.

Cần hiểu đúng mức bảo đảm: source vẫn có TODO về việc update grant record và tăng grant version chưa phải bulk atomic trong mọi backend; cache expiry/invalidation và persistence implementation vẫn là một phần của security correctness. Đây là lý do Metadata/Persistence là dependency của Security dù không thuộc phạm vi logic policy.

Source liên quan: [`Resolver.runResolvePass` và `bulkValidate`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/persistence/resolver/Resolver.java), [`AtomicOperationMetaStoreManager.persistNewGrantRecord`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/persistence/AtomicOperationMetaStoreManager.java).

## 15. Thuật toán quyết định quyền của internal authorizer

### 15.1 Operation → privilege requirements

[`RbacOperationSemantics`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/RbacOperationSemantics.java) ánh xạ mỗi `PolarisAuthorizableOperation` thành:

- tập privilege bắt buộc trên target;
- tập privilege bắt buộc trên secondary;
- cách rooting của resolved path.

### 15.2 Privilege được thỏa mãn thế nào?

[`PolarisAuthorizerImpl.hasTransitivePrivilege`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/PolarisAuthorizerImpl.java) đi qua toàn bộ resolved path từ parent xuống leaf. Một yêu cầu privilege `r` được thỏa nếu tồn tại:

- một entity `o` trên path target, có thể là ancestor hoặc leaf;
- một role `g` thuộc tập principal-role/catalog-role đã activate;
- một grant record từ `o` tới `g`;
- privilege được grant bằng `r` hoặc là super-privilege bao hàm `r`.

Viết hình thức:

```text
HasPrivilege(P, r, path)
  ⇔ ∃ o ∈ path,
       ∃ g ∈ ActivatedGrantees(P),
       ∃ q:
         Grant(g, o, q) ∧ Subsumes(q, r)
```

Cho operation `op`:

```text
ALLOW(P, op, targets, secondaries)
  ⇔ ∀ r ∈ RequiredTargetPrivileges(op),
       ∀ t ∈ targets: HasPrivilege(P, r, t)
   ∧ ∀ s ∈ RequiredSecondaryPrivileges(op),
       ∀ u ∈ secondaries: HasPrivilege(P, s, u)
```

Không thấy negative/deny grant trong internal `PolarisGrantRecord` model. Vì vậy internal RBAC là **allow-list**: tìm thấy đủ positive grants thì allow; thiếu bất kỳ grant nào thì deny.

### 15.3 Kế thừa theo resource hierarchy

Vì authorizer quét cả path, một table privilege được grant trên namespace ancestor có thể áp dụng cho table con; grant trên table leaf chỉ áp dụng table đó. Ví dụ:

```text
grant TABLE_READ_DATA on sales.finance to sales_reader

sales.finance.orders  → match qua namespace finance
sales.finance.invoice → match qua namespace finance
sales.public.events   → không match
```

Đừng nhầm **hierarchical traversal** với “mọi privilege ở catalog tự động bao hàm mọi privilege bên dưới”. Bao hàm còn phụ thuộc `SUPER_PRIVILEGES`; ví dụ `CATALOG_MANAGE_CONTENT` thỏa nhiều content privileges, còn `CATALOG_READ_PROPERTIES` không biến thành `TABLE_READ_DATA`.

### 15.4 Super-privilege

Internal authorizer duy trì map `SUPER_PRIVILEGES`: một privilege rộng có thể thỏa privilege hẹp. Các quan hệ dễ nhớ:

- `CATALOG_MANAGE_CONTENT` bao gồm metadata catalog/content và quyền đọc/ghi data;
- `CATALOG_MANAGE_METADATA` bao gồm metadata operations nhưng không thay quyền data độc lập;
- `*_FULL_METADATA` gom metadata privileges của đúng object type;
- `TABLE_WRITE_DATA` có thể thỏa yêu cầu `TABLE_READ_DATA` trong source hiện tại;
- `TABLE_FULL_METADATA` **không bao gồm** `TABLE_READ_DATA` hoặc `TABLE_WRITE_DATA` theo docs 1.7.0;
- trên `main`, `TABLE_MANAGE_STRUCTURE` bao hàm nhóm structural table updates nhưng không bao hàm snapshot/data operations.

Source authority cuối cùng là [`PolarisAuthorizerImpl.SUPER_PRIVILEGES`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/PolarisAuthorizerImpl.java); bảng mô tả công khai ở [Access Control 1.7.0](https://polaris.apache.org/releases/1.7.0/managing-security/access-control/#access-control-privileges).

## 16. Privilege taxonomy công khai trong Polaris 1.7.0

### 16.1 Table privileges

| Privilege | Cho phép |
|---|---|
| `TABLE_CREATE` | register/create table trong catalog/namespace scope |
| `TABLE_DROP` | drop table khỏi catalog |
| `TABLE_LIST` | liệt kê/kiểm tra khả kiến table |
| `TABLE_READ_PROPERTIES` | đọc metadata/properties table |
| `TABLE_WRITE_PROPERTIES` | sửa metadata/properties table |
| `TABLE_READ_DATA` | nhận short-lived storage credentials read-only |
| `TABLE_WRITE_DATA` | nhận short-lived storage credentials read+write |
| `TABLE_FULL_METADATA` | toàn bộ table metadata privileges, loại trừ hai data privileges |
| `TABLE_ATTACH_POLICY` | gắn policy vào table |
| `TABLE_DETACH_POLICY` | tháo policy khỏi table |

Điểm cần nhớ: “đọc table metadata” khác “được lấy credential để đọc data files”. `LOAD_TABLE` không yêu cầu giống `LOAD_TABLE_WITH_READ_DELEGATION`.

### 16.2 View privileges

| Privilege | Cho phép |
|---|---|
| `VIEW_CREATE` | tạo/register view |
| `VIEW_DROP` | drop view |
| `VIEW_LIST` | list view |
| `VIEW_READ_PROPERTIES` | đọc properties |
| `VIEW_WRITE_PROPERTIES` | sửa properties |
| `VIEW_FULL_METADATA` | toàn bộ view privileges |

### 16.3 Namespace privileges

| Privilege | Cho phép |
|---|---|
| `NAMESPACE_CREATE` | tạo namespace |
| `NAMESPACE_DROP` | drop namespace |
| `NAMESPACE_LIST` | list object/nested namespace |
| `NAMESPACE_READ_PROPERTIES` | đọc properties |
| `NAMESPACE_WRITE_PROPERTIES` | sửa properties |
| `NAMESPACE_FULL_METADATA` | toàn bộ namespace privileges |
| `NAMESPACE_ATTACH_POLICY` | gắn policy |
| `NAMESPACE_DETACH_POLICY` | tháo policy |

### 16.4 Catalog privileges

| Privilege | Cho phép |
|---|---|
| `CATALOG_MANAGE_ACCESS` | grant/revoke privilege trong catalog và catalog-role assignment |
| `CATALOG_MANAGE_CONTENT` | quản lý toàn bộ metadata + read/write data |
| `CATALOG_MANAGE_METADATA` | quản lý metadata catalog, catalog role, namespace, table |
| `CATALOG_READ_PROPERTIES` | list catalog và đọc properties |
| `CATALOG_WRITE_PROPERTIES` | sửa catalog properties |
| `CATALOG_ATTACH_POLICY` | gắn policy vào catalog |
| `CATALOG_DETACH_POLICY` | tháo policy khỏi catalog |

`CATALOG_MANAGE_CONTENT` theo docs bao hàm `CATALOG_MANAGE_METADATA`, `TABLE_FULL_METADATA`, `NAMESPACE_FULL_METADATA`, `VIEW_FULL_METADATA`, `TABLE_READ_DATA`, `TABLE_WRITE_DATA`, và read/write catalog properties.

### 16.5 Policy privileges

| Privilege | Cho phép |
|---|---|
| `POLICY_CREATE` | tạo policy dưới namespace |
| `POLICY_READ` | đọc content và metadata policy |
| `POLICY_WRITE` | cập nhật content/description |
| `POLICY_LIST` | list policy |
| `POLICY_DROP` | drop policy khi chưa attach |
| `POLICY_FULL_METADATA` | toàn bộ policy metadata privileges |
| `POLICY_ATTACH` | cho phép policy được attach vào entity |
| `POLICY_DETACH` | cho phép policy được detach |

Hai phía đều cần được mô hình hóa khi attach: quyền trên policy và quyền attach trên object nhận policy.

### 16.6 Properties không phải nơi giữ secret

Docs cảnh báo table/view properties là metadata có thể đọc được bởi principal có `*_READ_PROPERTIES` hoặc `*_FULL_METADATA`. Không lưu password, token, access key hay secret ở đó. [Cảnh báo chính thức](https://polaris.apache.org/releases/1.7.0/managing-security/access-control/#view-privileges).

## 17. Những privilege có trong source nhưng trang RBAC công khai không liệt kê hết

Trang Access Control 1.7.0 tập trung vào content-user privileges. Enum [`PolarisPrivilege`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/entity/PolarisPrivilege.java) ở source còn mô hình hóa đầy đủ management plane.

### 17.1 Service và role-edge privileges

- `SERVICE_MANAGE_ACCESS`: quyền quản trị service/root scope.
- `PRINCIPAL_ROLE_USAGE`: cạnh principal → principal role.
- `CATALOG_ROLE_USAGE`: cạnh principal role → catalog role.

Hai `*_USAGE` là dữ liệu cấu thành role graph, không phải business capability mà client thường yêu cầu trực tiếp.

### 17.2 Catalog lifecycle bổ sung

- `CATALOG_CREATE`, `CATALOG_DROP`, `CATALOG_LIST`, `CATALOG_FULL_METADATA`.
- Cùng với `CATALOG_READ_PROPERTIES`, `CATALOG_WRITE_PROPERTIES`, `CATALOG_MANAGE_METADATA`, `CATALOG_MANAGE_CONTENT`, `CATALOG_MANAGE_ACCESS`.

### 17.3 Đọc và quản lý grant

- Đọc grants: `PRINCIPAL_LIST_GRANTS`, `PRINCIPAL_ROLE_LIST_GRANTS`, `CATALOG_ROLE_LIST_GRANTS`, `CATALOG_LIST_GRANTS`, `NAMESPACE_LIST_GRANTS`, `TABLE_LIST_GRANTS`, `VIEW_LIST_GRANTS`.
- Quản lý grant trên securable: `CATALOG_MANAGE_GRANTS_ON_SECURABLE`, `NAMESPACE_MANAGE_GRANTS_ON_SECURABLE`, `TABLE_MANAGE_GRANTS_ON_SECURABLE`, `VIEW_MANAGE_GRANTS_ON_SECURABLE`, `POLICY_MANAGE_GRANTS_ON_SECURABLE`.
- Quản lý grant ở phía grantee: `PRINCIPAL_MANAGE_GRANTS_FOR_GRANTEE`, `PRINCIPAL_ROLE_MANAGE_GRANTS_FOR_GRANTEE`, `CATALOG_ROLE_MANAGE_GRANTS_FOR_GRANTEE`.

Sự phân đôi `ON_SECURABLE` và `FOR_GRANTEE` rất quan trọng. Một grant/revoke nối **hai security objects**; operation semantics có thể yêu cầu quyền ở phía object được bảo vệ, phía role nhận quyền, hoặc cả hai. Đây là cơ chế chống “tôi quản lý một phía nên có thể tự cấp bất kỳ quyền nào ở phía kia”.

### 17.4 Principal management

- `PRINCIPAL_CREATE`, `PRINCIPAL_DROP`, `PRINCIPAL_LIST`;
- `PRINCIPAL_READ_PROPERTIES`, `PRINCIPAL_WRITE_PROPERTIES`, `PRINCIPAL_FULL_METADATA`;
- `PRINCIPAL_MANAGE_GRANTS_ON_SECURABLE`, `PRINCIPAL_MANAGE_GRANTS_FOR_GRANTEE`;
- `PRINCIPAL_ROTATE_CREDENTIALS`, `PRINCIPAL_RESET_CREDENTIALS`.

### 17.5 Principal-role management

- `PRINCIPAL_ROLE_CREATE`, `PRINCIPAL_ROLE_DROP`, `PRINCIPAL_ROLE_LIST`;
- `PRINCIPAL_ROLE_READ_PROPERTIES`, `PRINCIPAL_ROLE_WRITE_PROPERTIES`, `PRINCIPAL_ROLE_FULL_METADATA`;
- `PRINCIPAL_ROLE_MANAGE_GRANTS_ON_SECURABLE`, `PRINCIPAL_ROLE_MANAGE_GRANTS_FOR_GRANTEE`.

### 17.6 Catalog-role management

- `CATALOG_ROLE_CREATE`, `CATALOG_ROLE_DROP`, `CATALOG_ROLE_LIST`;
- `CATALOG_ROLE_READ_PROPERTIES`, `CATALOG_ROLE_WRITE_PROPERTIES`, `CATALOG_ROLE_FULL_METADATA`;
- `CATALOG_ROLE_MANAGE_GRANTS_ON_SECURABLE`, `CATALOG_ROLE_MANAGE_GRANTS_FOR_GRANTEE`.

Đây là lý do mô tả Polaris chỉ bằng các quyền `TABLE_*` là thiếu: Security Layer bảo vệ cả control plane tạo identity, role và grant.

## 18. Fine-grained table-update privileges trên source `main`

Commit được nghiên cứu có thêm 18 privilege code từ 85 đến 102:

| Nhóm | Privileges |
|---|---|
| Identity/format | `TABLE_ASSIGN_UUID`, `TABLE_UPGRADE_FORMAT_VERSION` |
| Schema | `TABLE_ADD_SCHEMA`, `TABLE_SET_CURRENT_SCHEMA` |
| Partition/sort | `TABLE_ADD_PARTITION_SPEC`, `TABLE_REMOVE_PARTITION_SPECS`, `TABLE_ADD_SORT_ORDER`, `TABLE_SET_DEFAULT_SORT_ORDER` |
| Snapshot/ref | `TABLE_ADD_SNAPSHOT`, `TABLE_SET_SNAPSHOT_REF`, `TABLE_REMOVE_SNAPSHOTS`, `TABLE_REMOVE_SNAPSHOT_REF` |
| Location/properties/stats | `TABLE_SET_LOCATION`, `TABLE_SET_PROPERTIES`, `TABLE_REMOVE_PROPERTIES`, `TABLE_SET_STATISTICS`, `TABLE_REMOVE_STATISTICS` |
| Super-privilege structural | `TABLE_MANAGE_STRUCTURE` |

Feature config `ENABLE_FINE_GRAINED_UPDATE_TABLE_PRIVILEGES`, mặc định `true` trên source main, khiến handler phân rã từng Iceberg `MetadataUpdate` thành operation tương ứng. Nếu tắt, logic fallback dùng `TABLE_WRITE_PROPERTIES` thô hơn.

Ý nghĩa kiến trúc:

```text
UpdateTableRequest
  ├─ AddSchema       → TABLE_ADD_SCHEMA
  ├─ SetLocation     → TABLE_SET_LOCATION
  ├─ AddSnapshot     → TABLE_ADD_SNAPSHOT
  └─ SetProperties   → TABLE_SET_PROPERTIES

mọi update trong request đều phải được allow
```

`TABLE_MANAGE_STRUCTURE` bao hàm các thay đổi cấu trúc như schema/spec/sort/format, nhưng source test và super-privilege map cố ý không cho nó thay quyền snapshot. Đây là một bước dịch từ coarse-grained RBAC sang least privilege ở cấp loại metadata update.

Phần này thuộc **unreleased main** trong bản checkout, không có trong bảng privilege công khai 1.7.0 ở trên. Khi triển khai phải kiểm tra đúng release/config thay vì copy policy từ `main` sang 1.7.0 một cách máy móc.

## 19. Bảng operation → privilege quan trọng

Nguồn chính là [`RbacOperationSemantics`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/RbacOperationSemantics.java).

### 19.1 Namespace

| Operation | Required privilege |
|---|---|
| `LIST_NAMESPACES` | `NAMESPACE_LIST` |
| `CREATE_NAMESPACE` | `NAMESPACE_CREATE` |
| `LOAD_NAMESPACE_METADATA` | `NAMESPACE_READ_PROPERTIES` |
| `NAMESPACE_EXISTS` | `NAMESPACE_LIST` |
| `UPDATE_NAMESPACE_PROPERTIES` | `NAMESPACE_WRITE_PROPERTIES` |
| `DROP_NAMESPACE` | `NAMESPACE_DROP` |

### 19.2 Table

| Operation | Target privileges | Giải thích |
|---|---|---|
| `LIST_TABLES` | `TABLE_LIST` | list visibility |
| `CREATE_TABLE_DIRECT` | `TABLE_CREATE` | tạo metadata không xin storage write credential |
| `CREATE_TABLE_DIRECT_WITH_WRITE_DELEGATION` | `TABLE_CREATE` + `TABLE_WRITE_DATA` | tạo và xin credential ghi |
| `CREATE_TABLE_STAGED` | `TABLE_CREATE` | staged create |
| `CREATE_TABLE_STAGED_WITH_WRITE_DELEGATION` | `TABLE_CREATE` + `TABLE_WRITE_DATA` | staged + credential |
| `REGISTER_TABLE` | `TABLE_CREATE` | register metadata location |
| `REGISTER_TABLE_OVERWRITE` | `TABLE_FULL_METADATA` | overwrite registration |
| `LOAD_TABLE` | `TABLE_READ_PROPERTIES` | trả table metadata |
| `LOAD_TABLE_WITH_READ_DELEGATION` | `TABLE_READ_DATA` | metadata + read/list storage access |
| `LOAD_TABLE_WITH_WRITE_DELEGATION` | `TABLE_WRITE_DATA` | metadata + read/list/write storage access |
| `UPDATE_TABLE` | `TABLE_WRITE_PROPERTIES` | coarse-grained path |
| `UPDATE_TABLE_FOR_STAGED_CREATE` | `TABLE_CREATE` | finalize staged create |
| `DROP_TABLE_WITHOUT_PURGE` | `TABLE_DROP` | bỏ catalog entry |
| `DROP_TABLE_WITH_PURGE` | `TABLE_DROP` + `TABLE_WRITE_DATA` | còn xóa object storage |
| `TABLE_EXISTS` | `TABLE_LIST` | kiểm tra tồn tại là vấn đề visibility |
| `RENAME_TABLE` | source: `TABLE_DROP`; destination: `TABLE_LIST` + `TABLE_CREATE` | kiểm tra cả hai phía |
| `COMMIT_TRANSACTION` | `TABLE_WRITE_PROPERTIES` + `TABLE_CREATE` | coarse contract cho multi-table commit trên source |

Register có delegation cũng kết hợp `TABLE_CREATE`/`TABLE_FULL_METADATA` với `TABLE_READ_DATA` hoặc `TABLE_WRITE_DATA` tùy mode.

### 19.3 View

| Operation | Required privilege |
|---|---|
| list/create/register/load/replace/drop/exists | `VIEW_LIST` / `VIEW_CREATE` / `VIEW_CREATE` / `VIEW_READ_PROPERTIES` / `VIEW_WRITE_PROPERTIES` / `VIEW_DROP` / `VIEW_LIST` |
| rename | source `VIEW_DROP`; destination `VIEW_LIST` + `VIEW_CREATE` |

### 19.4 Metrics và notifications

- `REPORT_READ_METRICS` → `TABLE_READ_DATA`.
- `REPORT_WRITE_METRICS` → `TABLE_WRITE_DATA`.
- `SEND_NOTIFICATIONS` trên source hiện yêu cầu đồng thời các quyền `TABLE_CREATE`, `TABLE_WRITE_PROPERTIES`, `TABLE_DROP`, `NAMESPACE_CREATE`, `NAMESPACE_DROP`, vì tập required privileges được AND-combine.

Ngay cả endpoint “chỉ báo metrics” vẫn tiết lộ hoạt động trên table, nên source không coi nó là không cần quyền.

### 19.5 Catalog và identity management

| Operation family | Privilege family |
|---|---|
| list/create/get/update/delete catalog | `CATALOG_LIST/CREATE/READ_PROPERTIES/WRITE_PROPERTIES/DROP` |
| list/create/get/update/delete principal | `PRINCIPAL_LIST/CREATE/READ_PROPERTIES/WRITE_PROPERTIES/DROP` |
| rotate credential của principal khác / reset | `PRINCIPAL_ROTATE_CREDENTIALS` / `PRINCIPAL_RESET_CREDENTIALS`; self-rotate được handler cho phép, internal reset có special rule chỉ root |
| CRUD principal role | `PRINCIPAL_ROLE_*` |
| CRUD catalog role | `CATALOG_ROLE_*` |

### 19.6 Grant/revoke

Ví dụ source main:

```text
ADD_NAMESPACE_GRANT_TO_CATALOG_ROLE
  target: NAMESPACE_MANAGE_GRANTS_ON_SECURABLE

REVOKE_NAMESPACE_GRANT_FROM_CATALOG_ROLE
  target:    NAMESPACE_MANAGE_GRANTS_ON_SECURABLE
  secondary: CATALOG_ROLE_MANAGE_GRANTS_FOR_GRANTEE

ASSIGN_PRINCIPAL_ROLE
  target: PRINCIPAL_ROLE_MANAGE_GRANTS_ON_SECURABLE

REVOKE_PRINCIPAL_ROLE
  target:    PRINCIPAL_ROLE_MANAGE_GRANTS_ON_SECURABLE
  secondary: PRINCIPAL_MANAGE_GRANTS_FOR_GRANTEE
```

Không nên suy luận grant và revoke luôn đối xứng tuyệt đối. Changelog/source cho thấy một số semantics đã được tinh chỉnh theo phiên bản; policy phải bám đúng `RbacOperationSemantics` của binary đang chạy.

### 19.7 Policy attachment

Attach/detach kiểm tra hai phía:

```text
ATTACH_POLICY_TO_TABLE
  target policy: POLICY_ATTACH
  secondary table: TABLE_ATTACH_POLICY

DETACH_POLICY_FROM_NAMESPACE
  target policy: POLICY_DETACH
  secondary namespace: NAMESPACE_DETACH_POLICY
```

Như vậy người quản lý policy không tự động có quyền gắn policy vào mọi table; và người quản lý table cũng không tự động được dùng mọi policy.

## 20. Credential vending là điểm nối giữa Security và Storage

Credential vending không phải hậu quả tự động của việc được đọc metadata. Handler chọn operation khác nhau dựa vào client có yêu cầu access delegation hay không.

Luồng load table trong [`IcebergCatalogHandler`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandler.java):

```text
Không delegation:
  authorize LOAD_TABLE
  → cần TABLE_READ_PROPERTIES
  → không vend storage credential

Có delegation:
  thử LOAD_TABLE_WITH_WRITE_DELEGATION
  → có TABLE_WRITE_DATA: cấp READ + LIST + WRITE actions
  → nếu không: thử LOAD_TABLE_WITH_READ_DELEGATION
       → có TABLE_READ_DATA: cấp READ + LIST actions
       → nếu không: deny
```

Điều này giải thích quan hệ:

```text
Security decision                    Storage effect
TABLE_READ_PROPERTIES                chỉ metadata
TABLE_READ_DATA                      credential read/list ngắn hạn
TABLE_WRITE_DATA                     credential read/list/write ngắn hạn
```

Trước khi mint credential, source hiện tại còn phải xác định effective locations và storage actions. Threat model yêu cầu location/authorization/scope checks hoàn tất trước vending. Đây là ranh giới đã từng có lỗi bảo mật: [CVE-2026-42809](https://polaris.apache.org/community/security-advisories/cve-2026-42809/) mô tả staged-create ở các phiên bản trước 1.4.1 có thể mint credential trước location validation. Bài học kiến trúc là **authorize action thôi chưa đủ; phải validate resource boundary mà credential sẽ đại diện**.

## 21. Bootstrap root và service admin

Mỗi realm được bootstrap bởi [`AuthBootstrapUtil`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/AuthBootstrapUtil.java):

1. tạo internal root-container securable;
2. tạo principal tên `root`;
3. tạo principal role `service_admin`;
4. grant `PRINCIPAL_ROLE_USAGE` từ `service_admin` cho `root`;
5. grant `SERVICE_MANAGE_ACCESS` trên root-container cho `service_admin`;
6. trả root principal credentials.

```text
root principal
  └─ PRINCIPAL_ROLE_USAGE → service_admin
       └─ SERVICE_MANAGE_ACCESS → ROOT container
```

Root không phải một `if principalName == root then allow everything` đơn giản cho mọi operation. Phần lớn quyền được thỏa qua role/grant graph và super-privilege semantics. Source chỉ có special-case rõ ràng cho `RESET_CREDENTIALS`: `PolarisAuthorizerImpl` yêu cầu caller là root principal.

Credential bootstrap phải được rotate/bảo vệ như secret hạ tầng; không sử dụng credential mẫu của môi trường dev trong production.

## 22. External authorization với OPA

### 22.1 Vị trí kiến trúc

Khi `polaris.authorization.type=opa`, Polaris vẫn làm realm resolution và authentication. Thứ được thay là **policy decision**:

```text
Polaris handler
  → AuthorizationRequest
  → OpaPolarisAuthorizer
  → HTTP POST policy-uri
  → OPA evaluates Rego
  → { "result": { "allow": true|false } }
  → Polaris enforces result
```

Docs 1.7.0 gọi OPA integration là preview/beta và cảnh báo có thể có breaking changes. [OPA Integration](https://polaris.apache.org/releases/1.7.0/managing-security/external-pdp/opa/).

### 22.2 Input Polaris gửi OPA

[`OpaPolarisAuthorizer`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/extensions/auth/opa/src/main/java/org/apache/polaris/extension/auth/opa/OpaPolarisAuthorizer.java) dựng input gồm:

```json
{
  "input": {
    "actor": {
      "principal": "spark_etl",
      "roles": ["data_engineer"]
    },
    "action": "LOAD_TABLE_WITH_READ_DELEGATION",
    "resource": {
      "targets": [
        {
          "type": "TABLE_LIKE",
          "name": "orders",
          "parents": [
            {"type": "CATALOG", "name": "sales"},
            {"type": "NAMESPACE", "name": "finance"}
          ]
        }
      ],
      "secondaries": []
    },
    "context": {
      "requestId": "...",
      "realm": "production"
    }
  }
}
```

Mỗi intent được query riêng; tất cả phải allow. OPA nhận tên principal và **active principal roles**, action, target/secondary hierarchy, realm và request ID.

### 22.3 OPA thay thế chứ không cộng thêm internal RBAC

Comment trong source nói rõ OPA authorizer bypass built-in role-based authorization. Polaris không tính `PolarisPrivilege`/catalog-role grants rồi mới hỏi OPA. Policy OPA phải tự triển khai semantics phù hợp cho action và resource.

Hệ quả:

- Grant đã cấu hình trong internal RBAC không tự có tác dụng nếu policy OPA không đọc/tái hiện nó.
- OPA input hiện có active principal-role names, nhưng không gửi toàn bộ internal catalog-role/grant graph.
- Docs nói OPA hỗ trợ ABAC; tuy nhiên input model source hiện tại chỉ cung cấp actor/action/resource/context nêu trên. Muốn dùng thuộc tính phong phú hơn cần policy data bên OPA hoặc customization phù hợp, không nên giả định mọi JWT claim tự xuất hiện trong input.
- Các special rule nằm riêng trong internal `PolarisAuthorizerImpl`, như “chỉ root được reset credentials” và rotation-required precondition, không tự động được cộng thêm vào OPA decision. Policy/external enforcement phải định nghĩa quy tắc tương đương nếu deployment cần; input OPA hiện cũng không chứa toàn bộ internal principal properties. Đây là khác biệt implementation cần test, không chỉ là thay đổi cú pháp policy.

### 22.4 Fail-closed behavior

- HTTP response khác `200` → source trả deny.
- `result.allow` thiếu/sai → mặc định `false`.
- lỗi I/O/parse → ném runtime error; operation bảo vệ không được tiếp tục, nhưng client có thể nhận lỗi service thay vì `403`.

Nói chính xác: OPA path **không fail open**; dependency outage có thể biến thành availability failure.

### 22.5 Cấu hình OPA đáng chú ý

```properties
polaris.authorization.type=opa
polaris.authorization.opa.policy-uri=https://opa.example/v1/data/polaris/authz
polaris.authorization.opa.http.timeout=PT2S
polaris.authorization.opa.http.verify-ssl=true
```

OPA auth mặc định là `none`; có thể dùng static bearer token hoặc file-based bearer token có auto-refresh. Production nên dùng TLS verification, trust store đúng, secret mount thay vì hardcode, và thiết kế timeout/availability theo fail-closed. [Cấu hình OPA 1.7.0](https://polaris.apache.org/releases/1.7.0/managing-security/external-pdp/opa/#configuration-reference).

## 23. Ranger extension trên source `main`

Source hiện có `extensions/auth/ranger`; [README tại commit nghiên cứu](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/extensions/auth/ranger/README.md) yêu cầu Apache Ranger 2.8.0+ và cấu hình `polaris.authorization.type=ranger`.

Legacy flow của [`RangerPolarisAuthorizer`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/extensions/auth/ranger/src/main/java/org/apache/polaris/extension/auth/ranger/RangerPolarisAuthorizer.java):

1. map Polaris operation thành Ranger access semantics;
2. map target/secondary path và realm thành Ranger resource;
3. map principal/roles thành Ranger user info;
4. gửi multi-authorization request;
5. chỉ tiếp tục nếu kết quả tổng thể allow.

Tuy nhiên có caveat phiên bản quan trọng: method SPI mới `authorize(AuthorizationState, AuthorizationRequest)` trong source commit này vẫn ném `UnsupportedOperationException("authorize is not implemented yet")`; chỉ các overload legacy `authorizeOrThrow` có implementation. Đồng thời trang external PDP chính thức 1.7.0 chỉ liệt kê OPA.

Vì vậy Ranger nên được ghi nhận là **extension có trong source main, với migration gap ở intent-based SPI tại commit nghiên cứu**, không trình bày như một lựa chọn ổn định ngang OPA cho mọi endpoint/release. Trước production phải test đúng distribution, handler set và commit.

## 24. Error semantics và chống lộ thông tin

| Tình huống | HTTP thường gặp | Ý nghĩa |
|---|---:|---|
| thiếu/sai realm | `404` | `MissingOrInvalidRealm` |
| thiếu/sai/expired bearer token | `401` | chưa xác thực |
| principal/role claim không map được hợp lệ | `401` | authentication failure |
| identity hợp lệ nhưng thiếu privilege | `403` | authorization denied |
| internal token endpoint ở external mode | `501` | endpoint bị vô hiệu hóa |
| metastore không dùng được khi authentication | `503` | dependency failure, không giả thành bad credential |
| OPA không cho phép/non-200 | `403` hoặc service failure tùy loại lỗi | fail closed |

[`IcebergExceptionMapper`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/exception/IcebergExceptionMapper.java) map `ForbiddenException` → 403 và `NotAuthorizedException` → 401.

Hai nguyên tắc:

1. `401` trả lời “chưa thiết lập được identity đáng tin”, còn `403` trả lời “identity đã biết nhưng không có quyền”.
2. Existence cũng là thông tin. Vì vậy `TABLE_EXISTS` cần `TABLE_LIST`, `NAMESPACE_EXISTS` cần `NAMESPACE_LIST`; caller không có list visibility không nên dùng exists endpoint để dò tên object.

Client-facing denial của internal authorizer giữ message tương đối tổng quát; missing privilege chi tiết được log phía server. Log vẫn phải được bảo vệ vì có principal, role và resource context.

## 25. Bốn trace end-to-end

### 25.1 Internal token rồi load table với read delegation

```text
1. Client POST /oauth/tokens
   client_id=spark_etl
   scope=PRINCIPAL_ROLE:data_engineer

2. JWTBroker
   - validate form
   - match secret hash
   - phát JWT {sub, principalId, scope, exp, ...}

3. Client GET table với access delegation
   Authorization: Bearer <JWT>

4. RealmContextFilter chọn realm production

5. InternalAuthenticationMechanism verify JWT

6. DefaultAuthenticator
   - principal spark_etl tồn tại
   - data_engineer thật sự được grant
   - tạo PolarisPrincipal

7. Resolver
   - data_engineer → sales_reader catalog role
   - resolve sales.finance.orders và grants trên path

8. Handler thử LOAD_TABLE_WITH_WRITE_DELEGATION
   - thiếu TABLE_WRITE_DATA → không cấp write

9. Handler thử LOAD_TABLE_WITH_READ_DELEGATION
   - tìm TABLE_READ_DATA trên table/ancestor qua active catalog role
   - allow

10. Storage integration chỉ nhận READ + LIST actions
```

### 25.2 External OIDC

```text
1. IdP phát JWT có sub/name và enterprise roles
2. Quarkus chọn tenant, verify JWT
3. PrincipalMapper: sub/name → Polaris principal ID/name
4. PrincipalRolesMapper: enterprise role → PRINCIPAL_ROLE:data_engineer
5. DefaultAuthenticator đối chiếu principal + role với Polaris metastore
6. Handler/authorizer xử lý giống identity nội bộ từ đây trở xuống
```

Điểm hội tụ là `PolarisPrincipal`; downstream authorizer không cần biết JWT ban đầu do Polaris hay IdP phát.

### 25.3 Rename table

```text
request: sales.finance.orders → sales.archive.orders_2025

source path:
  cần TABLE_DROP

destination path:
  cần TABLE_LIST
  cần TABLE_CREATE

chỉ khi cả ba điều kiện đúng mới allow rename
```

Nếu chỉ kiểm tra source, caller có thể di chuyển object vào namespace không được tạo nội dung. Nếu chỉ kiểm tra destination, caller có thể lấy object nguồn mà mình không được drop. `RenameAuthorizationIntent` buộc mô hình hóa cả hai.

### 25.4 Grant privilege cho catalog role

```text
request:
  grant TABLE_READ_DATA
  on sales.finance
  to catalog-role sales_reader

authorization intent:
  target    = namespace sales.finance
  secondary = catalog-role sales_reader

resolve:
  target tồn tại trong đúng catalog
  grantee role tồn tại và thuộc đúng scope

authorize:
  kiểm tra grant-management semantics của operation

persist:
  ghi PolarisGrantRecord
  tăng grantRecordsVersion để cache được invalidate/refresh
```

Việc “ghi một row grant” chỉ xảy ra sau resolve và authorization; truy cập persistence trực tiếp từ internal code không tự là bằng chứng caller có quyền.

## 26. Security boundary với các layer khác

### 26.1 Với API/Protocol Layer

- API parse HTTP, nhưng Security quyết định identity và quyền.
- OAuth endpoint thuộc API surface; broker/credential validation thuộc Authentication.
- Handler phải chọn đúng operation theo semantics, đặc biệt khi request xin credential hoặc có secondary target.

### 26.2 Với Catalog Service Layer

- Handler là Policy Enforcement Point: gọi authorizer trước business mutation/read.
- `LocalIcebergCatalog` và table operations không nên được xem là nơi thay thế authorization.
- Fine-grained update logic dịch Iceberg `MetadataUpdate` thành nhiều authorization intents trước commit.

### 26.3 Với Metadata Management Layer

- Principal, role, entity hierarchy và grant record là security state.
- Resolver là cầu nối từ tên do request gửi sang entity identity đáng tin.
- Grant/policy management vừa là metadata operation vừa là security-sensitive operation.

### 26.4 Với Persistence Layer

- Realm scoping, transaction, entity version và grant-record version bảo vệ tính nhất quán của quyết định.
- Cache stale có thể trở thành security bug nếu revoke không được nhận ra; vì thế resolver validate version.
- Persistence trả được row không có nghĩa row đó được phép trả cho external caller.

### 26.5 Với Storage Integration Layer

- RBAC quyết định có được yêu cầu read/write data delegation không.
- Storage layer phải scope credential theo verified locations/actions.
- Location string là untrusted input cho đến khi qua structured/allowed-location/overlap checks.

### 26.6 Với Supporting Subsystems

- Events/audit cần ghi đủ principal, realm, action, decision, resource nhưng không ghi token/secret.
- Metrics phải tránh cardinality hoặc label làm lộ dữ liệu nhạy cảm.
- Background tasks dùng service identity cũng phải có mô hình authorization rõ; không được mặc định bypass chỉ vì là task nội bộ.

## 27. Những hiểu nhầm thường gặp

### “JWT có role admin là đủ”

Sai. `DefaultAuthenticator` còn kiểm tra role đó hiện được grant cho principal trong realm.

### “Có `TABLE_READ_PROPERTIES` là đọc được data”

Sai. Nó cho đọc metadata. Credential đọc data cần `TABLE_READ_DATA`.

### “`TABLE_FULL_METADATA` là toàn quyền table”

Sai theo docs 1.7.0. Nó loại trừ `TABLE_READ_DATA` và `TABLE_WRITE_DATA`.

### “Catalog role là global role”

Sai. Catalog role thuộc đúng một catalog và chỉ active khi resolve catalog đó.

### “OIDC thay toàn bộ user database Polaris”

Sai với default authenticator tại commit nghiên cứu. OIDC chứng minh identity; principal tương ứng vẫn phải được quản lý trong Polaris.

### “OPA chạy thêm sau RBAC”

Sai với implementation hiện tại. OPA authorizer thay built-in RBAC decision và policy OPA phải tự định nghĩa allow/deny.

### “Grant quyền chỉ cần kiểm tra người được grant”

Sai. Đây là quan hệ hai phía; intent và operation semantics có thể kiểm tra cả securable lẫn grantee để chống privilege escalation.

### “Rotate secret lập tức hủy mọi JWT”

Không thể kết luận vậy từ `JWTBroker` hiện tại. Secret mới chặn phát token bằng secret cũ; JWT đã phát chủ yếu chịu signature/expiry và kiểm tra principal/role hiện tại.

## 28. Checklist cấu hình production

### Realm

- Khai báo tập realm rõ ràng; production nên yêu cầu realm header thay vì silent default nếu có multitenancy.
- Test cùng principal/table name ở hai realm không cross-resolve.
- Không dùng realm header do reverse proxy tùy tiện cho client sửa nếu kiến trúc tenant routing yêu cầu proxy kiểm soát.

### Internal authentication

- Dùng RSA key pair cho production.
- Mọi replica phải dùng chung signing/verification keys.
- Mount private key bằng secret mechanism; giới hạn file permission và rotation procedure.
- Giữ token lifetime ngắn phù hợp rủi ro; mặc định là một giờ, không mặc nhiên là tối ưu cho mọi hệ thống.
- Principal chỉ yêu cầu role cần dùng trong scope, không luôn dùng `PRINCIPAL_ROLE:ALL`.
- Thu hồi khẩn cấp phải tính cả access token đã phát, không chỉ đổi client secret.

### OIDC

- Xác minh issuer, TLS, JWKS/public keys và audience theo cấu hình Quarkus/IdP.
- Ưu tiên immutable principal ID claim hơn display name có thể đổi.
- Filter/mapping chỉ nhận role namespace được quản trị; test role tương tự/regex edge cases.
- Tạo principal/role mapping tương ứng trong từng realm.
- Ở `external` mode, xác minh internal token endpoint thực sự trả `501`.

### Authorization/RBAC

- Tách principal role theo job function và catalog role theo catalog scope.
- Cấp data privileges riêng; đừng dùng `CATALOG_MANAGE_CONTENT` chỉ để cho đọc metadata.
- Test ancestor grants và table-specific exceptions.
- Với rename/attach/grant, test deny ở cả target và secondary.
- Sau revoke, test trên replica khác để phát hiện cache invalidation/config vấn đề.
- Theo đúng privilege set của release; không trộn fine-grained main với 1.7.0.

### OPA/Ranger

- OPA policy mặc định deny và có unit tests cho mọi operation mới.
- Dùng HTTPS/verify SSL; bảo vệ bearer token; theo dõi timeout và availability.
- Đảm bảo policy hiểu `targets`, `secondaries`, parent hierarchy, realm và every-intent-AND.
- Ranger phải test đúng source/distribution vì intent-based SPI chưa hoàn tất ở commit nghiên cứu.

### Secrets và storage

- Không đặt secret vào catalog/table/view properties.
- Không log bearer token, client secret, OPA bearer token hay vended cloud credentials.
- Validate location trước mọi write/vending; encode an toàn wildcard/expression ký tự cho provider policy.
- Chạy ít nhất 1.4.1 trở lên vì các advisory credential-vending/location đã được fix tại đó; thực tế nên dùng release được hỗ trợ mới nhất.

## 29. Các CVE chính thức và bài học kiến trúc

Trang [Known Security Vulnerabilities](https://polaris.apache.org/community/security-report/#known-security-vulnerabilities-cves) liệt kê bốn CVE được fix trong 1.4.1; tất cả ảnh hưởng `< 1.4.1`:

| CVE | Bản chất | Bài học cho Security Layer |
|---|---|---|
| [CVE-2026-42809](https://polaris.apache.org/community/security-advisories/cve-2026-42809/) | stage-create mint credential trước location validation | authorization và location validation phải hoàn tất trước vending |
| [CVE-2026-42810](https://polaris.apache.org/community/security-advisories/cve-2026-42810/) | wildcard trong name làm rộng S3 IAM policy | encode caller-controlled identifier theo ngôn ngữ policy đích |
| [CVE-2026-42811](https://polaris.apache.org/community/security-advisories/cve-2026-42811/) | CEL expression injection làm rộng GCS credential | không nội suy path thô vào policy expression |
| [CVE-2026-42812](https://polaris.apache.org/community/security-advisories/cve-2026-42812/) | `write.metadata.path` thoát location boundary | validate trước security-sensitive write, không chỉ trước persist/vend |

Các CVE cho thấy một điểm học thuật quan trọng: RBAC đúng vẫn chưa đủ nếu capability phát xuống hệ thống khác — ở đây là cloud credential — đại diện resource rộng hơn resource vừa được authorize.

## 30. Bản đồ source code để tự đọc tiếp

| Mục đích | Source chính |
|---|---|
| Realm filter/resolver | [`RealmContextFilter`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/context/RealmContextFilter.java), [`DefaultRealmContextResolver`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/context/DefaultRealmContextResolver.java) |
| Internal bearer authentication | [`InternalAuthenticationMechanism`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/internal/InternalAuthenticationMechanism.java) |
| Token endpoint | [`DefaultOAuth2ApiService`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/internal/service/DefaultOAuth2ApiService.java) |
| JWT broker/scope validation | [`JWTBroker`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/internal/broker/JWTBroker.java), [`TokenRequestValidator`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/internal/broker/TokenRequestValidator.java) |
| OIDC mapping | [`OidcPolarisCredentialAugmentor`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/external/OidcPolarisCredentialAugmentor.java) |
| Identity reconciliation | [`DefaultAuthenticator`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/DefaultAuthenticator.java), [`AuthenticatingAugmentor`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/auth/AuthenticatingAugmentor.java) |
| Principal object | [`PolarisPrincipal`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/PolarisPrincipal.java) |
| Authorization SPI | [`PolarisAuthorizer`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/PolarisAuthorizer.java), [`AuthorizationIntent`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/AuthorizationIntent.java) |
| Internal RBAC decision | [`PolarisAuthorizerImpl`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/PolarisAuthorizerImpl.java) |
| Operation mapping | [`RbacOperationSemantics`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/RbacOperationSemantics.java) |
| Privilege enum | [`PolarisPrivilege`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/entity/PolarisPrivilege.java) |
| Principal/role/path resolution | [`Resolver`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/persistence/resolver/Resolver.java), [`PolarisResolutionManifest`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/persistence/resolver/PolarisResolutionManifest.java) |
| Root bootstrap | [`AuthBootstrapUtil`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/polaris-core/src/main/java/org/apache/polaris/core/auth/AuthBootstrapUtil.java) |
| OPA | [`OpaPolarisAuthorizer`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/extensions/auth/opa/src/main/java/org/apache/polaris/extension/auth/opa/OpaPolarisAuthorizer.java) |
| Ranger | [`RangerPolarisAuthorizer`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/extensions/auth/ranger/src/main/java/org/apache/polaris/extension/auth/ranger/RangerPolarisAuthorizer.java) |
| Iceberg enforcement examples | [`IcebergCatalogHandler`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/runtime/service/src/main/java/org/apache/polaris/service/catalog/iceberg/IcebergCatalogHandler.java) |
| Threat model | [`SECURITY-THREAT-MODEL.md`](https://github.com/apache/polaris/blob/9da600803a540ae168580053c952f8ac6c947986/SECURITY-THREAT-MODEL.md) |

## 31. Cách học phần này theo thứ tự

1. Nắm bốn output: `RealmContext` → `PolarisCredential` → `PolarisPrincipal` → `AuthorizationDecision`.
2. Đọc internal flow trước vì nó phơi bày đầy đủ scope, JWT và active role.
3. Đọc `DefaultAuthenticator` để hiểu token role không tự tạo quyền.
4. Vẽ role graph principal → principal role → catalog role → securable.
5. Đọc `RbacOperationSemantics` trước `PolarisAuthorizerImpl`: một file trả lời “cần quyền gì”, file kia trả lời “tìm quyền đó thế nào”.
6. Đọc `Resolver` để hiểu path, catalog scope và cache/version.
7. Trace ba operation đại diện: load-with-credentials, rename, grant.
8. Cuối cùng mới so OPA/Ranger, vì chúng thay policy engine nhưng vẫn dùng identity/enforcement skeleton.

## 32. Tóm tắt cô đọng

Security Layer của Polaris có thể ghi nhớ bằng công thức:

```text
Realm
  + verified token
  + principal tồn tại
  + requested role thật sự được grant
  + operation semantics
  + resolved resource hierarchy
  + đủ positive grants/super-privileges trên mọi target và secondary
  = request được phép
```

Authentication của Polaris là sự kết hợp giữa cryptographic identity và metastore-managed identity. Authorization mặc định là hierarchical RBAC hai tầng role, với catalog role bị giới hạn theo catalog và privilege có thể được kế thừa theo ancestor path. Handler là điểm enforce: nó phải diễn đạt đúng operation/intents trước khi đọc, mutate hoặc vend credentials. OPA thay policy decision nội bộ; Ranger hiện là extension có caveat trên source main. Realm, cache consistency và storage credential scope là ba ranh giới khiến Security Layer liên kết với các layer khác nhưng vẫn giữ trách nhiệm riêng.

## 33. Tài liệu chính thức tham khảo

- [Apache Polaris 1.7.0 — Role-Based Access Control](https://polaris.apache.org/releases/1.7.0/managing-security/access-control/)
- [Apache Polaris 1.7.0 — Identity Providers](https://polaris.apache.org/releases/1.7.0/managing-security/external-idp/)
- [Apache Polaris 1.7.0 — Realm](https://polaris.apache.org/releases/1.7.0/realm/)
- [Apache Polaris 1.7.0 — External Policy Decision Point](https://polaris.apache.org/releases/1.7.0/managing-security/external-pdp/)
- [Apache Polaris 1.7.0 — OPA Integration](https://polaris.apache.org/releases/1.7.0/managing-security/external-pdp/opa/)
- [Apache Polaris 1.7.0 — Authentication with Helm](https://polaris.apache.org/releases/1.7.0/helm-chart/authentication/)
- [Apache Polaris 1.7.0 — Configuration Reference](https://polaris.apache.org/releases/1.7.0/configuration/configuration-reference/)
- [Apache Polaris — Security Report and Advisories](https://polaris.apache.org/community/security-report/)
- [Apache Polaris source — fixed commit used for this study](https://github.com/apache/polaris/tree/9da600803a540ae168580053c952f8ac6c947986)

## Đối chiếu cuối báo cáo — Bảy câu hỏi cốt lõi

Phần này nhìn **Polaris từ Security Layer**. Security là một nhóm trách nhiệm trong catalog server, không phải một catalog hay metastore độc lập.

### 1. Nó quản lý loại metadata nào?

Security sử dụng realm, principal, principal roles, catalog roles, grants và resource hierarchy để xác thực danh tính và đánh giá quyền. Cấu hình issuer/token validation và external policy provider cũng tham gia theo authentication/authorization mode. Các records bền vững được quản lý qua metastore; Security diễn giải chúng để quyết định allow/deny, không quản lý snapshot/manifests của bảng. Xem mục 4, 10 và 13. [Polaris RBAC](https://polaris.apache.org/releases/1.7.0/managing-security/access-control/)

### 2. Metadata persistence nằm ở đâu?

Entity, role và grant records của Polaris nằm trong metastore backend. Với internal authentication, dữ liệu kiểm tra client secret được persistence theo mô hình principal secrets; secret plaintext không phải table property để phân phối cho engine. Với external OIDC, IdP quản lý identity/credential phía IdP, còn Polaris thực hiện mapping và dùng trạng thái phân quyền tương ứng.

JWT được client giữ và gửi tới server là credential, không phải bản database chứa đầy đủ quyền hiện hành. Iceberg metadata/data persistence vẫn ở các lớp khác. Xem mục 8–10 và 16.

### 3. Engine resolve một table như thế nào?

Engine gửi request cho catalog/namespace/table trong context xác thực. Polaris xác định realm và principal, resolve target cùng hierarchy/relationships cần thiết, rồi authorizer đánh giá đúng operation trên các tài nguyên đó. Chỉ khi được phép, catalog handler mới thực hiện load hoặc mutation.

**Resolver xác định tài nguyên; authorizer quyết định được làm gì với tài nguyên.** Một path tồn tại hoặc một token hợp lệ chưa đủ để đọc bảng. Xem mục 6, 10, 12 và 19.

### 4. Read path và write/commit path như thế nào?

**Read:** xác thực → resolve/authorize operation đọc metadata hoặc đọc dữ liệu theo yêu cầu → catalog load → trả kết quả/credential phù hợp → engine đọc storage.

**Write:** xác thực → resolve → kiểm tra quyền theo loại updates và tài nguyên liên quan → Catalog Service kiểm tra metadata/concurrency và commit. Security cho phép mutation nhưng không thay thế kiểm tra stale state hoặc transaction của persistence. Sau đó, storage tiếp tục kiểm tra credential của thao tác file. Với nhiều target, phải thỏa toàn bộ các intent bắt buộc. Xem mục 12 và 19–20.

### 5. Table state/version được quản lý bởi catalog hay table format?

Security không định nghĩa lịch sử bảng. Iceberg quản lý mô hình snapshot/table metadata; Polaris catalog công bố trạng thái hiện hành. Entity/grant versions giúp kiểm soát freshness và concurrency của metadata quản trị, không phải snapshot ID.

Việc đổi grant hoặc revoke role làm thay đổi điều kiện truy cập, không tạo Iceberg snapshot. Ngược lại, một snapshot lịch sử còn tồn tại cũng không tự cho principal quyền đọc nó. Xem mục 16 và Chương 4.

### 6. Security và storage credential được xử lý ở đâu?

Trách nhiệm được chia thành ba bước:

1. **Authentication:** kiểm tra credential/token và ánh xạ vào identity Polaris.
2. **Authorization:** internal RBAC hoặc provider được chọn đánh giá operation trên resource; handler là điểm enforce.
3. **Storage Integration:** sau khi quyền và location hợp lệ, cấp credential ngắn hạn theo phạm vi/action cho client.

Catalog token không phải S3/Azure/GCS credential. Quyền đọc metadata không đồng nghĩa quyền đọc/ghi file. Credential storage đã phát hành có thời hạn riêng; thay đổi catalog grant không bảo đảm thu hồi tức thì mọi credential đang lưu tại client. Cloud policies, thời hạn credential và quyền được cấp ngoài catalog đều phải được xét. Xem mục 11, 18 và 20. [Vended credentials](https://polaris.apache.org/releases/1.7.0/vended-credentials/)

### 7. Điểm khác biệt cốt lõi của catalog này là gì?

Góc nhìn Security cho thấy Polaris kết hợp **realm isolation, identity mapping, RBAC hai tầng role và enforcement theo operation**, rồi nối quyết định đó với credential vending. Chính điểm nối giữa quyền metadata và phạm vi storage access là giá trị kỹ thuật cần hiểu. Nó không tự cung cấp row filtering/column masking trong mọi engine, và quyền cloud cấp quá rộng ngoài catalog có thể làm mất hiệu quả của mô hình kiểm soát này.
