# Protocol benchmark tối thiểu cho lựa chọn catalog

Ngày: **13/10/2026**. Đây là **thiết kế**, chưa cài hệ thống, chạy pilot/benchmark hoặc tạo kết quả. Toàn bộ số cấu hình, số bảng, tải và thời lượng dưới đây là **tham số lab đề xuất**, không phải yêu cầu Viettel hay số đo. Phải khóa manifest trước khi thực nghiệm; chưa thể nói deployment sẵn sàng chạy khi còn version/digest hoặc compatibility chưa xác minh.

## 1. Chọn 2–3 ứng viên theo ca, không chọn catalog thắng trước

**Ca P0 đề xuất để minh họa phương pháp:** Iceberg v2, read/write qua Iceberg REST, self-hosted, một storage dùng chung loại triển khai, một engine và một client chung; chưa yêu cầu federation hoặc branch workflow. Đây là giả định nghiên cứu cần mentor xác nhận. Nếu dự án cần Delta-first, managed AWS hoặc federation, phải đổi ca và shortlist trước khi chạy.

| Mã | Phương án lab đề xuất | Lý do vào khảo sát thực nghiệm | Điều kiện phải giải quyết trước khi chạy |
|---|---|---|---|
| P | Apache Polaris + Iceberg REST + persistence relational JDBC/PostgreSQL | Đối tượng phân tích sâu của đề tài; cấu hình server REST với persistence bền vững | Chọn release và docs tương ứng, schema/init đúng release; xác minh auth/storage/engine ở B0 |
| H | Hive Metastore + Iceberg REST servlet + PostgreSQL | Phương án so sánh kiến trúc có nguồn gốc HMS, có đường REST được tài liệu hóa | Chọn release thực sự có REST và quyền cần dùng; PostgreSQL/driver/schema được release hỗ trợ; bổ sung policy service nếu cần và tính toàn bộ chi phí |
| N — mở rộng | Nessie + Iceberg REST + JDBC2/PostgreSQL + một branch cố định | Khảo sát ảnh hưởng kiến trúc version store; branch workflow chỉ thử riêng nếu có yêu cầu | Xác minh đúng release; guide đang ghi REST experimental, phải ghi vào C15; không dùng khi ca cấm experimental mà chưa giải quyết được |

**Hai ứng viên tối thiểu đề xuất là P và H**, nhưng đây là shortlist để xác minh trong lab, chưa phải danh sách đủ điều kiện triển khai. Nếu H không đáp ứng đường tích hợp/quyền của ca, không giảm yêu cầu để giữ nó; xem lại một phương án khác trong sáu công nghệ. N có thể là ứng viên thứ hai/thứ ba nếu ca chấp nhận mức trưởng thành đường REST đã xác minh.

Căn cứ kỹ thuật đã đọc lại ngày 13/10/2026:

- [Polaris relational JDBC](https://polaris.apache.org/in-dev/unreleased/metastores/relational-jdbc/) có PostgreSQL; trang **unreleased**, không dùng trực tiếp làm cấu hình cho release cũ. [Release 1.8.0](https://polaris.apache.org/downloads/1.8.0/) là mốc tham khảo có release notes, **chưa được chọn/kiểm thử làm bộ version tương thích**.
- [HMS REST](https://hive.apache.org/docs/latest/admin/iceberg-rest-catalog/) mô tả REST, auth và authorization; đường `latest` cần đối chiếu release. Không dùng cấu hình anonymous của quickstart làm bằng chứng đáp ứng quyền.
- [Nessie Iceberg REST guide](https://projectnessie.org/guides/iceberg-rest/) đang ghi experimental. [Nessie 0.107.4 configuration](https://projectnessie.org/nessie-0-107-4/configuration/) có JDBC2/PostgreSQL và cảnh báo JDBC cũ deprecated; đây là tài liệu kiểm tra, chưa khóa version lab.
- [Unity Catalog UniForm](https://docs.unitycatalog.io/usage/tables/uniform/) chứng minh đường đọc Iceberg từ Delta UniForm trong trang này; chưa đủ bằng chứng để đưa vào cùng bài native Iceberg write. Không suy mọi tính năng UC OSS từ trang này.
- Nếu federation là B, cân nhắc [Gravitino IRC + backend được chỉ định](https://github.com/apache/gravitino/blob/main/docs/iceberg-rest-service.md?plain=1); đo backend trực tiếp và qua federation để hiểu thêm tầng, không coi hai deployment có cùng chức năng.
- Nếu AWS managed là yêu cầu, đưa Glue vào ca AWS với storage/region/network thực tương ứng; không đặt Glue remote cạnh catalog localhost rồi quy toàn bộ latency cho catalog. Chọn đúng API Glue hay REST và client/SDK; không trộn hai đường.

## 2. Profile P0 và các yếu tố cần khóa

### 2.1 Cấu hình đề xuất

| Thành phần | P0 đề xuất; phải xác nhận hoặc điều chỉnh đồng loạt trước chạy |
|---|---|
| Format | Iceberg format v2; schema `event_id: long`, `writer_id: int`, `payload: string`; unpartitioned; Parquet; codec và target file size giống nhau |
| Metadata fixture | 10 namespace × 10 table = 100 table; mỗi bảng đọc có 10 snapshot, mỗi snapshot thêm 1 file nhỏ; file khoảng 1 MiB. Ghi kích thước JSON/manifest thực tế, không chỉ số snapshot |
| Storage | Một implementation S3-compatible, cùng version/digest, endpoint, disk class, consistency mode và network path; prefix riêng cho mỗi alternative/run. Chính implementation còn TBD; phải qua B0 |
| Catalog | 1 instance, giới hạn đề xuất 2 vCPU/4 GiB; cùng mức durability và logging. Không dùng in-memory persistence |
| Persistence DB | PostgreSQL cùng major/minor được mọi deployment hỗ trợ, instance sạch độc lập, 2 vCPU/4 GiB; durable disk/flush settings cố định. Cùng DB không có nghĩa cùng schema/locking semantics |
| Driver | 2 vCPU/4 GiB riêng; cùng Java/Iceberg client, HTTP stack và build; đo CPU/queue để không nhầm bottleneck driver là catalog |
| Engine | Spark dùng B0 và xác minh dữ liệu; khóa Spark/Scala/Iceberg runtime/Java tương thích. Không chạy Spark query trong timed API loop |
| Storage service | Ngân sách đề xuất 2 vCPU/4 GiB nếu lab tự host; cùng giới hạn giữa các run; không chạy các ứng viên đồng thời |
| Auth/policy | Bật cấu hình thực sự đáp ứng profile quyền. Các phương án có thể khác cơ chế; giữ cùng yêu cầu, token validity và quy mô policy, ghi dịch vụ phụ thuộc |
| TLS/network | Cùng trạng thái TLS, proxy, vị trí và số hop nếu khả thi; ghi RTT baseline và overhead instrumentation |
| Retry/timeouts | Cùng chính sách client nếu hỗ trợ: proposal tối đa 3 attempts cho lỗi cho phép retry, backoff 100/200 ms; request timeout 5 s, logical deadline 15 s. Đây là tham số lab, không phải SLA. Ghi retry nội bộ server/DB riêng; không retry mù indeterminate |

Ngân sách service ở bảng **không bao gồm** OS/VM, IdP, policy service hoặc Spark. Kiểm kê tổng tài nguyên trước khi chọn P0; nếu máy không đủ, giảm đồng loạt và ghi revision. Không khởi động swap rồi diễn giải đó là giới hạn scale của sản phẩm. Thử tuần tự từng phương án. Sidecar bắt buộc là một phần chi phí cấu hình; báo cả tài nguyên core catalog và tổng hệ thống phụ thuộc. Có thể thêm một bài fixed-total-budget sau này; không khẳng định P0 là so sánh tổng chi phí bằng nhau.

### 2.2 Kiểm soát nhiễu

| Biến | Cách kiểm soát | Cách báo khi không thể đồng nhất |
|---|---|---|
| Format/metadata | Cùng schema, format features, số snapshot/file, độ sâu namespace; seed giống | Đo payload/metadata bytes vì cấu trúc do server tạo có thể khác; không gọi dữ liệu byte-identical |
| Engine/client | Cùng engine/client/version và flags; fixture và validation tách khỏi timed loop | Nếu native client khác REST, chuyển sang thí nghiệm tích hợp riêng, không gộp chart API |
| Storage | Cùng service/config/hardware; prefix khác, fixture tương đương | Ghi số GET/PUT và latency storage; server commit có thể gồm I/O metadata, không suy thời gian CPU catalog |
| Backend catalog | Cùng loại/version DB nếu hỗ trợ; disk/flush/tài nguyên đồng mức, DB reset per run | Backend/schema/transaction là một phần kiến trúc được đánh giá; không loại nó khỏi deployment latency |
| Cache | B1 bypass cache ở driver bằng request thật, xác minh request count; chuẩn hóa warm-up; không gửi cache-busting headers chỉ cho một bên | Cache nội bộ catalog/DB còn là một phần cấu hình. Restart service là process-cold, không phải OS/DB/storage-cold |
| Token/permissions | Token còn hiệu lực cho bài steady state; số principal/policy tương đương; grant/revoke riêng | Ghi refresh/signing/vending; không trộn anonymous và authenticated thành kết luận triển khai |
| Tài nguyên và host | Quota rõ, cùng disk/network, chạy tuần tự, đo throttling/GC/CPU/IO; seed thứ tự ứng viên | Nếu host noisy, đánh dấu run và áp quy tắc rerun đã định; không chỉ bỏ các lần chậm |
| Concurrency/retry | Cùng offered load/in-flight limit, policy client; tách 1 attempt và logical operation | Đếm cả retry server nếu có telemetry; thiếu telemetry phải ghi phạm vi quan sát |
| Metadata growth | Fixture restore giữa run; B2 dùng số operation cố định và cùng phân bố | Không dùng state đã phình ở ứng viên chạy sau; ghi snapshot/metadata bytes trước/sau |

Tuning cho phép có giới hạn công sức bằng nhau, ghi mọi thay đổi. Giữ kết quả cấu hình ban đầu nếu đã đo; không lựa các thiết lập nhanh nhất riêng cho ứng viên mong muốn mà giấu chi phí tuning.

## 3. Ranh giới đo và log

Ba loại thời gian phải tách:

1. **Catalog API attempt latency:** từ driver gửi HTTP đến nhận đủ response; chứa network, proxy, auth, catalog và backend/storage phụ thuộc của request. Không gọi đây là thời gian xử lý thuần của catalog.
2. **Logical metadata operation latency:** từ bắt đầu thao tác đến kết quả cuối, gồm refresh, retry, backoff và I/O của client nếu thao tác cần. Với commit, đo giai đoạn tạo file data/manifest riêng.
3. **Engine/query elapsed time:** chỉ dùng kiểm tra tích hợp hoặc báo riêng như end-to-end. Không quy toàn bộ scan/planning/scheduling/execution cho catalog; không lấy tổng query trừ một số tùy ý để ước lượng catalog.

Đồng hồ monotonic ở driver cho latency. Log: run/config/requirement/scenario IDs; logical_op_id; attempt_id; writer/table/ref; expected snapshot; file/event IDs; start/end; status class; retry/backoff; bytes; returned metadata/snapshot; error; trace ID; auth identity đã ẩn thông tin nhạy cảm. Operation ID trong test là cơ chế quan sát, **không tự tạo idempotency server**.

Kết quả phân loại ít nhất: success, expected conflict, validation/auth denial, transport/server error, timeout/indeterminate. Goodput = số logical operation thành công duy nhất trên thời gian đo; request throughput phải ghi rõ gồm attempts. Không cộng retry vào số commit hữu ích, không chỉ vẽ latency của success rồi giấu timeout hoặc conflict.

## 4. Các kịch bản tối thiểu

B0 là kiểm thử chức năng trước benchmark. B1–B3 là đo/kiểm tra metadata. B4 là probe vận hành tối thiểu cho self-hosted, không phải chứng minh HA/DR. Mỗi kịch bản dưới đây có purpose/config/workload/metrics/oracle/decision. Chỉ có tham số đầu vào, chưa có kết quả.

### B0 — Đường tích hợp và quyền

- **Mục đích:** kiểm tra cấu hình có đủ tư cách vào bài so sánh; C01–C05/C09/C10.
- **Cấu hình:** P0, Spark và client thực, tài khoản writer, reader và unauthorized; mỗi identity có quyền catalog/storage được ghi rõ. Dùng namespace và prefix riêng.
- **Workload:** tạo namespace/table; append dữ liệu xác định; đọc; đổi schema theo thao tác yêu cầu; list/rename/drop chỉ trên fixture; reader thử ghi; unauthorized thử load/list/write; token sai/hết hạn; revoke theo thời gian hiệu lực được tài liệu hóa; kiểm tra storage prefix đúng/sai. Thử engine thứ hai nếu ca yêu cầu, còn không để mở rộng.
- **Chỉ số:** pass/fail/unknown từng test; lỗi và trace; thời gian triển khai/chỉnh cấu hình; độ trễ hiệu lực revoke nếu cần. Không dùng số test pass như điểm sản phẩm.
- **Oracle:** schema, event IDs, checksum, snapshot và location khớp fixture; thao tác được phép có hiệu ứng, thao tác cấm không có hiệu ứng; account reader không vô tình cầm credentials toàn quyền storage. Direct storage access xét theo IAM thực: credential vending không tự chặn credential quyền rộng đã cấp bên ngoài. Drop/purge/cleanup được xác minh theo semantics, không mặc định xóa catalog entry phải xóa data.
- **Đưa vào quyết định:** B thất bại → loại cấu hình hoặc sửa rồi chạy lại; thiếu khả năng quan sát → UNKNOWN. Có thể chạy performance để chẩn đoán một cấu hình chưa đạt nhưng không đưa nó vào shortlist đủ điều kiện.

### B1 — Đọc metadata và phát hiện giới hạn tải

- **Mục đích:** C03/C08: độ trễ load/list và goodput ở quy mô metadata đã định; tìm tải làm queue/latency tăng.
- **Cấu hình:** P0; driver REST chung gửi request thực, không engine query; fixture không có writer; token warm; HTTP connections tái sử dụng giống nhau. Server/DB cache warm sau cùng workload warm-up.
- **Workload:** đo load-table và list-tables riêng, không gộp percentile. Load-table: chọn bảng uniform theo seed trong 100 bảng. List-tables: duyệt đủ trang một namespace, page-size yêu cầu 5 để bài có thể đi qua nhiều trang; ghi actual page count/bytes và cả latency từng page lẫn một lượt list hoàn chỉnh. Nếu hỗ trợ pagination khác nhau, đó là khác biệt phải báo. Ba mức offered rate khởi đầu 5/20/50 logical ops/s; tối đa 32 in-flight. Pilot điều chỉnh dải cho cả hai phương án rồi khóa. Một block measured 3 phút sau warm-up đề xuất 1 phút, kéo dài warm-up nếu chưa ổn định.
- **Chỉ số:** achieved rate, success/error/timeout, p50/p95 (p99 chỉ khi đủ mẫu/độ ổn định), scheduler lag, queue, bytes/response, CPU/RAM/GC/DB I/O và storage GET. Không gọi mức cuối là saturation nếu chưa quan sát được.
- **Oracle:** load trả đúng UUID/schema/location/snapshot của fixture; parse mọi response, không chỉ HTTP 200. List trên fixture tĩnh trả đúng tập bảng quyền được thấy, không thiếu/trùng qua trang. Audit deterministically một số response và kiểm tra mọi ID/status; ghi tỷ lệ coverage. Mọi sai lệch mở điều tra, không chỉ coi là request nhanh.
- **Đưa vào quyết định:** có SLO → kiểm tra tại đúng tải/quy mô mục tiêu; chỉ ưu tiên tốc độ khi mức chênh có ý nghĩa và bất định đủ nhỏ. Chưa có SLO → cung cấp đường latency–goodput, không tự gán PASS production. Driver không đạt schedule thì chưa quy giới hạn cho server.

Open-loop scheduler ghi cả thời điểm dự kiến phát và thời điểm phát thực; queue/dispatch delay không bị bỏ khỏi latency trải nghiệm. Nếu dùng closed-loop phải ghi rõ, không dùng nó để kết luận đáp ứng offered rate hoặc che coordinated omission.

### B2 — Commit không tranh chấp

- **Mục đích:** C06/C08: chi phí công bố metadata và goodput khi writer không tranh cùng bảng.
- **Cấu hình:** P0; cùng Iceberg client/REST adapter; data files Parquet khoảng 1 MiB sinh trước, file ID riêng theo logical op. Driver tạo manifest/metadata bằng thư viện đúng format; không handcraft payload sai. Đo build/upload và publish riêng, ghi storage I/O server trong publish.
- **Workload:** 1 và 4 writers, mỗi writer sở hữu bảng riêng; tổng 100 append logical ops/run, schema/format cố định, không overwrite/delete/compaction/expire. Cùng số thao tác hữu ích giúp so metadata growth. Restore state trước mỗi run; ghi mức backlog và độ tăng metadata.
- **Chỉ số:** attempt latency ở endpoint commit; logical latency gồm refresh/retry; goodput; số attempts/success; conflict ngoài dự kiến; errors/indeterminate; bytes/PUT và CPU/DB. 100 logical ops là pilot, chưa đủ bảo đảm precision của tail percentile.
- **Oracle:** append-only với event ID và file path duy nhất: mỗi logical append được xác nhận phải hiện đúng một lần trong trạng thái đọc cuối, không mất/nhân đôi event; đọc manifest bằng client độc lập và scan Spark sau timed phase. Đối chiếu logical success với snapshot history. Orphan file chưa được tham chiếu không tự là committed data. Nếu có indeterminate, phân giải trước khi dùng kiểm tra tập bằng nhau.
- **Đưa vào quyết định:** vi phạm invariant được xác nhận là FAIL cấu hình; conflict hợp lệ không phải corruption; latency/goodput chỉ so ở cùng semantics/durability. Không khẳng định hiệu năng CPU catalog riêng từ commit path chứa I/O storage.

### B3 — Ghi đồng thời, conflict và retry

- **Mục đích:** C06/C08: phân biệt conflict hợp lệ, chi phí retry và mất cập nhật.
- **Cấu hình:** P0; một bảng hot, cùng logical transaction boundary. Nessie nếu tham gia dùng một branch cố định; không thay bài single-table bằng branch commit nhiều bảng.
- **Workload A — strict requirement:** hai writer chuẩn bị hai snapshot khác nhau cùng dựa trên ref `main` tại snapshot s. Gửi đồng thời hai request với `assert-ref-snapshot-id` cho s, đều đổi ref sang snapshot mới; tắt client retry. Bắt đầu đề xuất 20 cặp độc lập, dùng bảng/reset thích hợp giữa cặp. Phải xác minh release hỗ trợ request/requirement trước khi coi đây là oracle chung.
- **Workload B — logical append có retry:** 2 rồi 4 writer, mỗi writer 25 append ID duy nhất vào cùng bảng; conflict được refresh/rebase khi semantics cho phép, tối đa policy chung; không overwrite/delete. Log toàn bộ attempts, files và kết quả cuối. Không yêu cầu chỉ một logical append thành công vì các append hợp lệ có thể lần lượt được retry rồi cùng thành công.
- **Chỉ số:** expected conflicts/attempts, committed logical ops, retry distribution, p95 logical latency nếu đủ mẫu, fairness theo writer, unresolved ops, metadata growth; không chỉ tổng HTTP error rate.
- **Oracle:** A — khi mọi request đều hợp lệ, không có actor khác và có progress, đúng một request strict có thể công bố; cả hai công bố dù cùng điều kiện đã mất hiệu lực là phản ví dụ cần xác nhận. Hai request đều lỗi không chứng minh violation atomicity, cần phân loại availability/setup. B — tập ID của append acknowledged có mặt đúng một lần; retry không nhân đôi logical append; không xem final state là đủ để chứng minh mọi mô hình isolation. Nếu timeout/5xx không rõ trạng thái, read-back/snapshot history để phân giải, không tự gọi là abort và gửi append mới cùng dữ liệu.
- **Đưa vào quyết định:** semantics/invariant bắt buộc vi phạm → FAIL; retry overhead là đánh đổi performance, không tự là FAIL. Phân biệt thiếu oracle, lỗi driver và lỗi cấu hình/server trước khi quy trách nhiệm.

Thiết kế A lấy căn cứ hẹp từ [Iceberg REST OpenAPI](https://raw.githubusercontent.com/apache/iceberg/main/open-api/rest-catalog-open-api.yaml): requirement của ref và phân biệt conflict/unknown. Bản `main` cần được ghim commit phù hợp release; endpoint có trong spec không chứng minh server triển khai. Các workload/oracle cụ thể là đề xuất của người thiết kế, chưa thực nghiệm.

### B4 — Restart catalog và phân giải commit không rõ kết quả

- **Mục đích:** C06/C07/C12: kiểm tra durability của commit đã ack và khả năng phục hồi sau lỗi process.
- **Cấu hình:** P0, persistent DB/storage giữ nguyên; một proxy cùng vị trí cho mọi ứng viên nếu cần fault injection; không xóa volume hoặc phá dữ liệu người dùng.
- **Workload:** 2 writers append ID riêng, 1 reader; đề xuất tối thiểu 30 s steady state, restart một process catalog tại marker được log rồi quan sát tối đa 120 s sau restart. Các thời lượng chỉ là cửa sổ lab, không phải RTO. Thêm case proxy chuyển tiếp commit rồi giữ/bỏ response để tạo client timeout; giữ khả năng điều tra kết quả thật. Chạy fault từng loại riêng, bắt đầu 3 lượt độc lập nếu đủ nguồn lực.
- **Chỉ số:** thời gian từ injection đến khi thao tác chức năng phục hồi ổn định (proposal 10 probes liên tiếp cách 1 s); số success/error/indeterminate; thời gian phân giải; số ack mất nếu có; giờ công/runbook. Health endpoint không thay probe load/commit.
- **Oracle:** mọi append được ack trước lỗi còn đọc được sau phục hồi theo workload append-only; không metadata trỏ tới object không tồn tại; op chưa rõ được đối chiếu ID/manifest/history. Response mất có thể vẫn commit: không tự retry như transaction mới. Không phân giải được thì giữ UNKNOWN, không ép số mất dữ liệu bằng 0. Cửa sổ quan sát hết mà chưa phục hồi phải ghi chưa quan sát phục hồi, không báo RTO = 120 s.
- **Đưa vào quyết định:** so với recovery requirement nếu có; nếu không, báo phạm vi lỗi đã kiểm tra. Không suy restart một process = HA, backup/restore, DB failover, DR hoặc RPO toàn hệ thống. Các yêu cầu đó cần bài riêng và trở thành bắt buộc nếu có trong ca.

### B5 — Migration/exit nhỏ: bắt buộc có điều kiện

- **Mục đích:** C02/C10/C14: kiểm tra khả năng chuyển một tập bảng và công chuyển, khi ca thực tế có migration.
- **Cấu hình:** source/target xác định, cùng format/storage nếu dùng metadata-only migration; 5 bảng lab có schema evolution và snapshot history. Chỉ dùng bản sao fixture. Không cho hai catalog ghi cùng bảng cùng lúc.
- **Workload:** inventory/checksum → dừng writer → thực hiện đường migration được tài liệu hóa → validate target → thay client endpoint → đọc và append tại target. Đo rollback riêng: rollback trước target write và sau target write có rủi ro khác nhau; không coi đổi endpoint về là tự đồng bộ source. Nếu không có register/import phù hợp, thiết kế rewrite/migration khác và ghi chi phí.
- **Chỉ số:** thời gian từng bước, downtime, thao tác thủ công, giờ công, bytes copied, đối tượng/quyền/lịch sử không chuyển được.
- **Oracle:** UUID nếu được yêu cầu bảo toàn, schema/partition/snapshot và data checksum; permissions phải ánh xạ lại và thử deny; location không bị đổi sai; writer ownership duy nhất; sau target append vẫn đọc đúng. Không đòi copy byte-identical mọi metadata nếu protocol cho phép biến đổi hợp lệ; kiểm tra semantics cần giữ.
- **Đưa vào quyết định:** requirement bảo toàn/downtime/rollback không đạt → FAIL phương án migration; thiếu migration path → UNKNOWN hoặc FAIL theo bằng chứng, không mặc định miễn phí. Kết quả chỉ áp dụng cặp source–target đã thử.

## 5. Run matrix, pilot và thống kê

Mức tối thiểu để lập kế hoạch cho **mỗi ứng viên**, trước khi mở rộng:

| Bài | Số cell đầu vào | Repetitions khởi đầu | Vai trò |
|---|---:|---:|---|
| B0 | Một bộ functional/security test theo requirements | Rerun test bị ảnh hưởng khi sửa config | Gate |
| B1 | 2 thao tác × 3 offered rates = 6 | 3 block độc lập/cell | Pilot và đo đọc; tối thiểu khoảng 72 phút nếu warm 1 + measured 3 phút |
| B2 | 2 writer-counts, không tranh chấp | 3 run/cell | Pilot commit |
| B3 | Strict pairs; append với 2/4 writers | 3 run cho mỗi workload setting | Correctness/concurrency |
| B4 | Restart; response-loss | Khởi đầu 3 lượt mỗi fault | Probe recovery; không ước lượng xác suất lỗi hiếm |
| B5 | Một cặp source–target nếu requirement cần | Dry run rồi rehearsal xác nhận | Migration, không benchmark toàn bộ 6×5 cặp |

Đây là run budget ban đầu, **không phải chứng minh đủ mẫu**. Nếu tài nguyên không đủ, ưu tiên oracle/gates rồi B1/B2 tại tải liên quan; hạ phạm vi kết luận thay vì dựng số liệu. Không nhân toàn bộ cache × size × load × engine × backend thành factorial lớn. Hotspot, 1.000 bảng, process-cold, second engine, scale-out và branch/federation là các biến thể có câu hỏi cụ thể.

Sau pilot:

1. Kiểm tra harness có phát đủ tải, thời gian warm-up, xu hướng drift, số sample và correlation ở mức request/run/restart.
2. Chọn dải tải và độ chính xác cần để phân biệt với SLO hoặc chênh lệch có ý nghĩa. Chạy thêm ở cell sát ranh giới quyết định; không lặp mọi cell vô hạn.
3. Báo từng run, không chỉ gộp hàng nghìn request thành mẫu độc lập. Nếu dùng interval/bootstrap phải chọn đơn vị/block phù hợp correlation, công bố cách tính; p99 không báo chắc chắn khi thiếu dữ liệu.
4. Không kết luận A nhanh hơn nếu bất định và nhiễu chưa cho phép. Với SLO, chỉ PASS khi dữ liệu đáp ứng quy tắc bất định đã thống nhất; trường hợp giáp ngưỡng là UNKNOWN/đo thêm. Không tự áp công thức thống kê sau khi xem bên nào thắng.
5. Ghi protocol deviations, failed runs và lý do rerun. Seed/đảo thứ tự P–H giữa block để giảm time trend; lưu host metrics. Lưu toàn bộ dữ liệu, không chỉ đồ thị đẹp.

Nguyên tắc phân biệt workload/adapter kế thừa [YCSB](https://doi.org/10.1145/1807128.1807152); pilot/lặp/bất định từ [Kalibera & Jones](https://doi.org/10.1145/2464157.2464160); history và giới hạn suy correctness tham khảo [Elle](https://doi.org/10.14778/3430915.3430918); công bố cấu hình/variation từ [Hoefler & Belli](https://doi.org/10.1145/2807591.2807644). Không dùng nguyên YCSB KV hoặc Elle checker khi chưa chứng minh mapping catalog sang model của chúng.

## 6. Gắn kết quả với quyết định và chi phí

Mỗi kết quả gắn C-ID và R-ID, bao gồm phạm vi, unit, uncertainty và evidence ID. Trước benchmark viết recommendation tạm thời và câu hỏi đang thiếu; sau benchmark ghi gate nào đổi, trade-off nào rõ hơn hoặc confidence nào thay đổi. Không thay đổi khuyến nghị cũng là kết quả hợp lệ.

Ước tính chi phí ở cùng kỳ H và mức dịch vụ: `TCO(H) = triển khai + migration + chi phí hạ tầng/dịch vụ trong H + nhân công vận hành trong H + exit nếu thuộc phạm vi`. Liệt kê các hạng mục loại trừ và rủi ro chưa lượng hóa, tránh double count. Giữ giờ công riêng nếu chưa có đơn giá; thực hiện thấp/cơ sở/cao chỉ khi có căn cứ cho khoảng. Tính chênh lệch so baseline cùng scope; không gọi chênh lệch lab là tiết kiệm thực tế. Chi phí API/bytes có thể dùng usage đo từ benchmark nhưng cần workload production được xác nhận để ngoại suy.

## 7. Điều kiện sẵn sàng chạy và dừng

Trước khi chạy: xác nhận ca P0 hoặc thay ca; chọn 2–3 ứng viên; ghim release/image digest/client/storage/DB; điền manifest; duyệt oracle; định nghĩa acceptance thresholds nếu có; kiểm tra tài nguyên; xác định seed/reset, auth và privacy logs. Chưa đáp ứng thì chỉ hoàn thành thiết kế, không nhận benchmark reproducible đã sẵn sàng.

Dừng một cell nếu oracle tìm phản ví dụ cần điều tra, driver mất khả năng tạo tải, môi trường sai manifest hoặc budget đạt giới hạn đã định. Giữ log và trạng thái, không xóa để biến thành run thành công. Dừng toàn nghiên cứu thực nghiệm khi đã trả lời các bất định quyết định trong ngân sách, hoặc công bố những câu hỏi còn inconclusive. Không cần benchmark cả sáu catalog nếu tài liệu và yêu cầu đã loại hợp lệ; không loại vì chưa có thời gian triển khai rồi ghi sản phẩm kém.
