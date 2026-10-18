# Protocol benchmark tối thiểu cho lựa chọn catalog

Phiên bản **v2 sau thẩm định, 13/10/2026**. Đây là **thiết kế**, chưa cài hệ thống, chạy pilot/benchmark hoặc tạo kết quả. [Các lỗi của v1 và cách sửa](review-2026-10-13/review.md). Mọi số cấu hình/số bảng/tải/thời lượng còn là **seed cho pilot**, không phải SLO, quy mô đại diện hay thiết kế suy luận thống kê đã được xác nhận. Manifest, kế hoạch phân tích và kiểm chứng harness phải được khóa trước lượt đo chính thức.

## 1. Chọn 2–3 ứng viên theo ca, không chọn catalog thắng trước

**Ca P0 đề xuất để minh họa phương pháp:** Iceberg v2, read/write qua Iceberg REST, self-hosted, một storage dùng chung loại triển khai, một engine và một client chung; chưa yêu cầu federation hoặc branch workflow. Đây là giả định nghiên cứu cần mentor xác nhận. Nếu dự án cần Delta-first, managed AWS hoặc federation, phải đổi ca và shortlist trước khi chạy.

| Mã | Phương án lab đề xuất | Lý do vào khảo sát thực nghiệm | Điều kiện phải giải quyết trước khi chạy |
|---|---|---|---|
| P | Apache Polaris + Iceberg REST + persistence relational JDBC/PostgreSQL | Đối tượng phân tích sâu của đề tài; cấu hình server REST với persistence bền vững | Chọn release và docs tương ứng, schema/init đúng release; xác minh auth/storage/engine ở B0 |
| H | Hive Metastore + Iceberg REST servlet + PostgreSQL | Phương án so sánh kiến trúc có nguồn gốc HMS, có đường REST được tài liệu hóa | Chọn release thực sự có REST và quyền cần dùng; PostgreSQL/driver/schema được release hỗ trợ; bổ sung policy service nếu cần và tính toàn bộ chi phí |
| N — mở rộng | Nessie + Iceberg REST + JDBC2/PostgreSQL + một branch cố định | Khảo sát ảnh hưởng kiến trúc version store; branch workflow chỉ thử riêng nếu có yêu cầu | Xác minh đúng release; guide đang ghi REST experimental, phải ghi vào C15; không dùng khi ca cấm experimental mà chưa giải quyết được |

**P, H và N là các ví dụ cấu hình cần khảo sát, không phải cặp benchmark đã chọn.** Ghi một hàng cho cả sáu công nghệ: đáp ứng/không đáp ứng/chưa xác minh chức năng của ca; mức trưởng thành của đúng đường tích hợp; khả năng làm lab; lý do chọn/không chọn vào mẫu. Chọn hai ứng viên sau bước này; ứng viên thứ ba chỉ khi giải quyết một đánh đổi khác. Không có điều kiện self-hosted/REST được xác nhận thì không dùng P0 để loại managed/native API.

Trước so sánh lập **bảng hợp đồng chức năng**: thao tác, transaction boundary, read visibility, auth/storage policy, durability, retry semantics và phạm vi metadata. Nếu hai cấu hình không cùng hợp đồng cần dùng, giữ so sánh như các kiến trúc thay thế có chức năng/chi phí khác nhau, không gộp thành bảng tốc độ thuần catalog.

Hai câu hỏi nghiên cứu riêng: (Q-common) cùng thao tác và yêu cầu, deployment nào đáp ứng trong profile cụ thể? (Q-capability) chức năng riêng như branch/federation/managed operations giải quyết nhu cầu nào, với công/chi phí gì? Common REST core chỉ trả lời Q-common; không đại diện toàn bộ Nessie, HMS, Gravitino, Glue hoặc UC OSS. Mỗi ứng viên không được đo vẫn có hồ sơ tài liệu, không được ghi FAIL chỉ vì không được chọn vào mẫu.

Căn cứ kỹ thuật đã đọc lại ngày 13/10/2026:

Các link sau chỉ là bằng chứng để **định vị khả năng**. Trước chạy cần release-tag/commit permalink, image digest và thao tác xác nhận. Áp cùng chuẩn chứng cứ cho mọi ứng viên; nhãn experimental trên một guide chưa đủ để xếp toàn sản phẩm kém hơn các sản phẩm có maturity chưa được kiểm tra.

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
| Retry/timeouts | Tách B3 strict: một attempt, tắt HTTP/SDK/client replay và kiểm tra wire trace. Logical append dùng retry sau confirmed conflict theo contract, không retry mù indeterminate. Seed tối đa 3 attempts, request cap 5 s, backoff 100/200 ms; deadline logical D còn phải chọn sau pilot, mỗi attempt cap=min(5 s, thời gian còn lại), không hứa đủ 3 attempts trong 15 s |

Ngân sách service ở bảng **không bao gồm** OS/VM, IdP, policy service hoặc Spark. Kiểm kê tổng tài nguyên trước khi chọn P0; nếu máy không đủ, giảm đồng loạt và ghi revision. Không khởi động swap rồi diễn giải đó là giới hạn scale của sản phẩm. Thử tuần tự từng phương án. Sidecar bắt buộc là một phần chi phí cấu hình; báo cả tài nguyên core catalog và tổng hệ thống phụ thuộc. Có thể thêm một bài fixed-total-budget sau này; không khẳng định P0 là so sánh tổng chi phí bằng nhau.

### 2.2 Kiểm soát nhiễu

| Biến | Cách kiểm soát | Cách báo khi không thể đồng nhất |
|---|---|---|
| Format/metadata | Cùng schema, format features, số snapshot/file, độ sâu namespace; seed giống | Đo payload/metadata bytes vì cấu trúc do server tạo có thể khác; không gọi dữ liệu byte-identical |
| Engine/client | Cùng engine/client/version và flags; fixture và validation tách khỏi timed loop | Nếu native client khác REST, chuyển sang thí nghiệm tích hợp riêng, không gộp chart API |
| Storage | Cùng service/config/hardware; prefix khác, fixture tương đương | Ghi số GET/PUT và latency storage; server commit có thể gồm I/O metadata, không suy thời gian CPU catalog |
| Backend catalog | Cùng loại/version DB nếu hỗ trợ; disk/flush/tài nguyên đồng mức, DB reset per run | Backend/schema/transaction là một phần kiến trúc được đánh giá; không loại nó khỏi deployment latency |
| Cache | B1 gửi request thật và xác minh wire/request count; khóa cùng quy trình preconditioning sau pilot, đo time series; không mặc định một phút làm nóng là đủ | Cache catalog/DB là một phần cấu hình. Restart service chỉ là process restart, không phải mọi cache lạnh; 100 bảng fit cache không đại diện mọi quy mô |
| Token/permissions | Token còn hiệu lực cho bài steady state; số principal/policy tương đương; grant/revoke riêng | Ghi refresh/signing/vending; không trộn anonymous và authenticated thành kết luận triển khai |
| Tài nguyên và host | Quota rõ, cùng disk/network, chạy tuần tự, đo throttling/GC/CPU/IO; seed thứ tự ứng viên | Nếu host noisy, đánh dấu run và áp quy tắc rerun đã định; không chỉ bỏ các lần chậm |
| Concurrency/retry | Cùng offered load/in-flight limit, policy client; tách 1 attempt và logical operation | Đếm cả retry server nếu có telemetry; thiếu telemetry phải ghi phạm vi quan sát |
| Metadata growth | Fixture restore giữa run; B2 dùng số operation cố định và cùng phân bố | Không dùng state đã phình ở ứng viên chạy sau; ghi snapshot/metadata bytes trước/sau |

Tuning cho phép có giới hạn công sức bằng nhau, ghi mọi thay đổi. Giữ kết quả cấu hình ban đầu nếu đã đo; không lựa các thiết lập nhanh nhất riêng cho ứng viên mong muốn mà giấu chi phí tuning.

**Phạm vi suy luận:** cùng CPU/RAM hoặc PostgreSQL chưa tạo thí nghiệm cô lập hiệu ứng của mã catalog. DB schema, policy service, I/O và cache là thành phần deployment. Cùng một host còn có tranh chấp CPU/disk giữa các service dù dùng quota. Nếu có bottleneck storage/driver/host, báo đó là giới hạn của thí nghiệm; muốn quy nguyên nhân cần trace/span hoặc thí nghiệm thay một yếu tố. Không trừ số đo query/storage khác run để tạo thời gian catalog giả. Một scale-point không chứng minh scalability; nếu C08 cần scale, thêm ít nhất một quy mô liên quan khác và vẫn giới hạn phạm vi ngoại suy.

## 3. Ranh giới đo và log

Ba loại thời gian phải tách:

1. **Catalog API attempt latency:** từ driver gửi HTTP đến nhận đủ response; chứa network, proxy, auth, catalog và backend/storage phụ thuộc của request. Không gọi đây là thời gian xử lý thuần của catalog.
2. **Logical metadata operation latency:** từ bắt đầu thao tác đến kết quả cuối, gồm refresh, retry, backoff và I/O của client nếu thao tác cần. Với commit, đo giai đoạn tạo file data/manifest riêng.
3. **Engine/query elapsed time:** chỉ dùng kiểm tra tích hợp hoặc báo riêng như end-to-end. Không quy toàn bộ scan/planning/scheduling/execution cho catalog; không lấy tổng query trừ một số tùy ý để ước lượng catalog.

Đồng hồ monotonic ở driver cho latency. Log: run/config/requirement/scenario IDs; logical_op_id; attempt_id; writer/table/ref; expected snapshot; file/event IDs; start/end; status class; retry/backoff; bytes; returned metadata/snapshot; error; trace ID; auth identity đã ẩn thông tin nhạy cảm. Operation ID trong test là cơ chế quan sát, **không tự tạo idempotency server**.

Kết quả phân loại ít nhất: success, expected conflict, validation/auth denial, transport/server error, timeout/indeterminate. Goodput = số logical operation thành công duy nhất trên thời gian đo; request throughput phải ghi rõ gồm attempts. Không cộng retry vào số commit hữu ích, không chỉ vẽ latency của success rồi giấu timeout hoặc conflict.

Khóa mẫu số: ghi `scheduled`, `admitted`, `sent_attempts`, `acknowledged_success`, `definitive_reject`, `unknown`, `late_resolved`. B1 báo số ack success hoàn tất trong cửa sổ/T và bảng cohort các logical ops được lên lịch trong cửa sổ với giai đoạn drain riêng; không cộng completion muộn vào tử số rồi vẫn chia T. B2/B3 là fixed-work batch: goodput = số logical op ack thành công / thời gian từ bắt đầu batch đến kết quả cuối/deadline của batch, ghi cả failure/unknown và backlog. Không gọi đây là steady-state capacity.

### 3.1 Đủ điều kiện harness và oracle trước so sản phẩm

Kiểm tra đồng hồ/counters, wire attempts thực, response validation, reset fixture và lỗi parser. Oracle phải nhận ra fixture hợp lệ và các bản sao có lỗi cấy có chủ đích: thiếu ID đã ack, ID bị lặp, dữ liệu của op đã reject, snapshot cũ, mất response. Đây là kế hoạch kiểm tra harness, **chưa chạy**. Ghi seed/coverage; checksum/manifest scan ngoài timed phase, tránh overhead kiểm tra trở thành bottleneck. Một phản ví dụ phải được tái hiện/phân giải harness–client–server–storage trước khi quy lỗi cho catalog.

Với append-only không có actor khác/GC/rollback, fixture ánh xạ mỗi logical operation tới tập event IDs duy nhất của nó. O là event IDs ban đầu; A là event IDs của các ops đã ack; R là event IDs của các ops đã xác nhận mọi attempt không công bố; U là event IDs của các ops chưa phân giải. Operation ID, file path và event ID được lưu riêng, không trộn kiểu trong phép so tập. Sau quiescence và fresh read phù hợp visibility contract, gọi V là tập event IDs quan sát:

- O∪A phải nằm trong V; V không chứa ID ngoài O∪A∪U; V không chứa ID thuộc R.
- Mỗi event ID xuất hiện một lần và payload/schema/checksum khớp fixture nếu giao thức client của bài thử cam kết không replay append thành transaction mới; nếu duplicate do replay của harness thì không kết luận catalog vi phạm exactly-once.
- Op có một attempt chưa rõ trạng thái vẫn ở U, kể cả attempt sau trả lỗi; phản hồi conflict không xóa khả năng attempt trước đã commit.
- Khi U chưa rỗng, không ép V=O∪A, không tự coi U là mất dữ liệu. Với overwrite/delete hoặc branch rollback phải thay oracle theo history; oracle này không áp dụng.

### 3.2 Hợp đồng tải và queue

Seed max in-flight=32 là giới hạn harness, không là khả năng catalog. Khóa trước đo: hàng đợi hữu hạn, chính sách từ chối ở driver, deadline tính từ scheduled time, và thời gian drain. Khi hết slot, giữ scheduled event và ghi dispatch delay hoặc admission failure; không âm thầm giảm offered rate. Báo scheduled-to-terminal latency song song API latency; mọi timeout/admission failure có mẫu số riêng. Nếu deadline quá ngắn khiến population bị censor, không gọi p95 của success là p95 của mọi request. Chưa chứng minh driver/storage không giới hạn thì chỉ kết luận deployment đáp ứng/không đáp ứng profile, chưa xác định bottleneck catalog.

## 4. Các kịch bản tối thiểu

B0, B1, B2 và B1V là bộ lõi cho ca read/write một bảng. B3 dùng khi concurrency có trong ca; B4 chỉ khi fault/recovery liên quan; B5 khi migration liên quan. Capability test bắt buộc nếu chức năng riêng là lý do khuyến nghị. Mỗi bài phải có R-ID hoặc một câu hỏi phương pháp rõ; không tự chạy toàn bộ mọi biến thể. Các số ở workload chỉ là seed pilot.

### B0 — Đường tích hợp và quyền

- **Mục đích:** kiểm tra cấu hình có đủ tư cách vào bài so sánh; C01–C05/C09/C10.
- **Cấu hình:** P0, Spark và client thực, tài khoản writer, reader và unauthorized; mỗi identity có quyền catalog/storage được ghi rõ. Dùng namespace và prefix riêng.
- **Workload:** tạo namespace/table; append dữ liệu xác định; đọc; đổi schema theo thao tác yêu cầu; list/rename/drop chỉ trên fixture; reader thử ghi; unauthorized thử load/list/write; token sai/hết hạn; revoke theo thời gian hiệu lực được tài liệu hóa; kiểm tra storage prefix đúng/sai. Thử engine thứ hai nếu ca yêu cầu, còn không để mở rộng.
- **Chỉ số:** pass/fail/unknown từng test; lỗi và trace; thời gian triển khai/chỉnh cấu hình; độ trễ hiệu lực revoke nếu cần. Không dùng số test pass như điểm sản phẩm.
- **Oracle:** schema, event IDs, checksum, snapshot và location khớp fixture; thao tác được phép có hiệu ứng, thao tác cấm không có hiệu ứng; account reader không vô tình cầm credentials toàn quyền storage. Direct storage access xét theo IAM thực: credential vending không tự chặn credential quyền rộng đã cấp bên ngoài. Drop/purge/cleanup được xác minh theo semantics, không mặc định xóa catalog entry phải xóa data.
- **Đưa vào quyết định:** B thất bại → loại cấu hình hoặc sửa rồi chạy lại; thiếu khả năng quan sát → UNKNOWN. Có thể chạy performance để chẩn đoán một cấu hình chưa đạt nhưng không đưa nó vào shortlist đủ điều kiện.

### B1 — Đọc metadata và phát hiện giới hạn tải

- **Mục đích:** C03/C08: độ trễ load/list và goodput ở quy mô metadata đã định; tìm tải làm queue/latency tăng.
- **Cấu hình:** P0; driver REST chung gửi request thực, không engine query; fixture không có writer; token còn hiệu lực; HTTP connections tái sử dụng giống nhau. Cùng quy trình preconditioning, trạng thái cache thực ghi từ telemetry nếu quan sát được; không mặc định warm-up đã hội tụ.
- **Workload:** đo load-table và list-tables riêng, không gộp percentile. Load-table: chọn bảng uniform theo seed trong 100 bảng. List-tables: duyệt đủ trang một namespace, page-size yêu cầu 5 để bài có thể đi qua nhiều trang; ghi actual page count/bytes và cả latency từng page lẫn một lượt list hoàn chỉnh. Nếu hỗ trợ pagination khác nhau, đó là khác biệt phải báo. Ba mức offered rate khởi đầu 5/20/50 logical ops/s; tối đa 32 in-flight. Pilot điều chỉnh dải cho cả hai phương án rồi khóa. Một block measured 3 phút sau warm-up đề xuất 1 phút, kéo dài warm-up nếu chưa ổn định.
- **Chỉ số:** achieved rate, success/error/timeout, p50/p95 (p99 chỉ khi đủ mẫu/độ ổn định), scheduler lag, queue, bytes/response, CPU/RAM/GC/DB I/O và storage GET. Không gọi mức cuối là saturation nếu chưa quan sát được.
- **Oracle:** load trả đúng UUID/schema/location/snapshot của fixture; parse mọi response, không chỉ HTTP 200. List trên fixture tĩnh trả đúng tập bảng quyền được thấy, không thiếu/trùng qua trang. Audit deterministically một số response và kiểm tra mọi ID/status; ghi tỷ lệ coverage. Mọi sai lệch mở điều tra, không chỉ coi là request nhanh.
- **Đưa vào quyết định:** có SLO → kiểm tra tại đúng tải/quy mô mục tiêu; chỉ ưu tiên tốc độ khi mức chênh có ý nghĩa và bất định đủ nhỏ. Chưa có SLO → cung cấp đường latency–goodput, không tự gán PASS production. Driver không đạt schedule thì chưa quy giới hạn cho server.

Open-loop scheduler ghi cả thời điểm dự kiến phát và thời điểm phát thực; queue/dispatch delay không bị bỏ khỏi latency trải nghiệm. Nếu dùng closed-loop phải ghi rõ, không dùng nó để kết luận đáp ứng offered rate hoặc che coordinated omission.

### B1V — Visibility từ client khác sau commit

- **Mục đích:** kiểm tra C06 freshness/read-after-write đã bị thiếu ở v1; phân biệt trạng thái cuối với khả năng nhìn thấy cập nhật tại thời điểm cần.
- **Cấu hình:** một writer, một reader độc lập cùng quyền; cùng bảng/ref; run 1 dùng fresh session/request xác minh không client cache, run 2 dùng cache policy dự kiến nếu requirement cần. Không rollback/expire/actor khác.
- **Workload:** writer append marker riêng, nhận ack rồi phát barrier qua coordinator; reader chỉ bắt đầu load/refresh sau barrier, ghi từng snapshot/marker và thời điểm quan sát. Lặp chuỗi ngắn seed 20 commit, reset per run. Chỉ thêm đọc đồng thời/đa bảng khi cần hợp đồng tương ứng.
- **Chỉ số:** số lần đọc post-ack còn cũ, thời gian đến khi thấy marker, timeout/cửa sổ quan sát hết; tách API path và client cache path.
- **Oracle:** marker đã ack phải xuất hiện theo hợp đồng visibility đã được xác minh. Nếu contract bảo đảm fresh read ngay thì stale response sau barrier là phản ví dụ cần điều tra; nếu bounded staleness thì dùng bound được xác nhận. Chưa có contract/bound chỉ ghi observations và UNKNOWN. Snapshot ID không được suy thứ tự số học; theo lineage/marker, không so `id_new > id_old`.
- **Đưa vào quyết định:** gate freshness nếu requirement có; nếu chỉ khám phá thì không kết luận linearizability toàn hệ thống. Một chuỗi read-after-write không kiểm chứng mọi history concurrent.

### B2 — Commit không tranh chấp

- **Mục đích:** C06/C08: chi phí công bố metadata và goodput khi writer không tranh cùng bảng.
- **Cấu hình:** P0; cùng Iceberg client/REST adapter; data files Parquet khoảng 1 MiB sinh trước, file ID riêng theo logical op. Driver tạo manifest/metadata bằng thư viện đúng format; không handcraft payload sai. Đo build/upload và publish riêng, ghi storage I/O server trong publish.
- **Workload:** giữ **4 bảng** và cùng initial snapshots trong cả setting 1/4 writers; seed tổng **100 append, 25 append/bảng**. Một writer đi round-robin 4 bảng; bốn writer mỗi người sở hữu một bảng. Không overwrite/delete/compaction/expire. Số bảng, số append/bảng và kích thước file cố định; concurrency là yếu tố thay đổi, interleaving/DB contention là hệ quả cần báo. Warm-up trên fixture khác, restore fixture đo trước mỗi run; báo theo vị trí append trên từng bảng để không giấu metadata growth.
- **Chỉ số:** attempt latency ở endpoint commit; logical latency gồm refresh/retry; goodput; số attempts/success; conflict ngoài dự kiến; errors/indeterminate; bytes/PUT và CPU/DB. 100 logical ops là pilot, chưa đủ bảo đảm precision của tail percentile.
- **Oracle:** áp dụng O/A/R/U/V tại §3.1, kiểm tra cả missing, duplicate và extra/rejected IDs. Đọc manifest bằng client xác minh và scan Spark ngoài timed phase; đối chiếu logical success với history. Orphan file chưa được tham chiếu không là committed data. Chưa phân giải U thì kết quả oracle từng thuộc tính có thể inconclusive, không tự tuyên bố mọi append đúng.
- **Đưa vào quyết định:** vi phạm invariant được xác nhận là FAIL cấu hình; conflict hợp lệ không phải corruption; latency/goodput chỉ so ở cùng semantics/durability. Không khẳng định hiệu năng CPU catalog riêng từ commit path chứa I/O storage.

### B3 — Ghi đồng thời, conflict và retry

- **Mục đích:** C06/C08: phân biệt conflict hợp lệ, chi phí retry và mất cập nhật.
- **Cấu hình:** P0; một bảng hot, cùng logical transaction boundary. Nessie nếu tham gia dùng một branch cố định; không thay bài single-table bằng branch commit nhiều bảng.
- **Workload A — strict requirement:** hai writer chuẩn bị hai snapshot khác nhau cùng dựa trên ref `main` tại snapshot s. Gửi đồng thời hai request với `assert-ref-snapshot-id` cho s, đều đổi ref sang snapshot mới; tắt client retry. Bắt đầu đề xuất 20 cặp độc lập, dùng bảng/reset thích hợp giữa cặp. Phải xác minh release hỗ trợ request/requirement trước khi coi đây là oracle chung.
- **Workload B — logical append có retry:** giữ cùng initial state và **100 logical append/run** trên một bảng: 2 writers × 50 hoặc 4 writers × 25. File/metadata payload tương đương; conflict refresh/rebase chỉ theo contract và policy đã khóa. Không overwrite/delete. Ghi wire attempts, files, reject/unknown và metadata growth. Nhiều logical append có thể lần lượt thành công hợp lệ; completion count thấp vì retry budget hết không tự là lỗi correctness.
- **Chỉ số:** expected conflicts/attempts, committed logical ops, retry distribution, p95 logical latency nếu đủ mẫu, fairness theo writer, unresolved ops, metadata growth; không chỉ tổng HTTP error rate.
- **Oracle:** A — safety: **tối đa một** request có thể công bố với cùng strict precondition và hai snapshot đích khác nhau, không actor khác. Liveness/progress kiểm tra riêng; cả hai lỗi chưa chứng minh vi phạm atomicity. Tắt và xác minh mọi lớp replay bằng trace; backend nội bộ không được bỏ precondition đã hỏng. B — dùng oracle §3.1; duplicate cần phân loại client replay hay server behavior. Timeout/5xx giữ unknown đến khi phân giải, không xem đó là abort. Final state hợp lệ không chứng minh mọi isolation model.
- **Đưa vào quyết định:** semantics/invariant bắt buộc vi phạm → FAIL; retry overhead là đánh đổi performance, không tự là FAIL. Phân biệt thiếu oracle, lỗi driver và lỗi cấu hình/server trước khi quy trách nhiệm.

Thiết kế A lấy căn cứ hẹp từ [Iceberg REST OpenAPI](https://raw.githubusercontent.com/apache/iceberg/main/open-api/rest-catalog-open-api.yaml): requirement của ref và phân biệt conflict/unknown. Bản `main` cần được ghim commit phù hợp release; endpoint có trong spec không chứng minh server triển khai. Các workload/oracle cụ thể là đề xuất của người thiết kế, chưa thực nghiệm.

### B4 — Restart catalog và phân giải commit không rõ kết quả

- **Mục đích:** C06/C07/C12: kiểm tra durability của commit đã ack và khả năng phục hồi sau lỗi process.
- **Cấu hình:** P0, persistent DB/storage giữ nguyên; một proxy cùng vị trí cho mọi ứng viên nếu cần fault injection; không xóa volume hoặc phá dữ liệu người dùng.
- **Workload:** nếu recovery là câu hỏi của ca, chọn trước loại lỗi: **kill process** khác graceful restart; giữ DB/storage. Sau preconditioning, fault theo operation marker cố định thay vì chỉ 30 s để tránh khác lượng dữ liệu trước lỗi; seed cửa sổ quan sát 120 s, không phải RTO. Response-loss là bài mở rộng riêng: proxy nhận đủ response thành công upstream rồi chặn downstream, tạo ack mất có ground truth; dùng cùng proxy trong control run để biết overhead. Không gộp hai lỗi thành một kết quả phục hồi.
- **Chỉ số:** ghi riêng lần probe load/commit thành công đầu tiên và cửa sổ ổn định sau đó. Seed 10 probes cách 1 s là quy tắc quan sát chưa xác nhận, không tự cộng 9 s thành RTO hệ thống. Polling làm thời điểm phục hồi bị giới hạn độ phân giải; báo bracket last-fail/first-success, errors/unknown và giờ công. Health endpoint không thay chức năng.
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

Các seed dưới đây chỉ phục vụ **pilot**, không là yêu cầu đủ mẫu hoặc lịch phải chạy toàn bộ. Lượt đo chính thức chọn cell theo requirements sau pilot và dùng dữ liệu mới:

| Bài | Số cell đầu vào | Repetitions khởi đầu | Vai trò |
|---|---:|---:|---|
| B0 | Một bộ functional/security test theo requirements | Rerun test bị ảnh hưởng khi sửa config | Gate |
| B1 | 2 thao tác × 3 offered rates = 6 | 3 block độc lập/cell | Pilot và đo đọc; tối thiểu khoảng 72 phút nếu warm 1 + measured 3 phút |
| B2 | 2 writer-counts, không tranh chấp | 3 run/cell | Pilot commit |
| B1V | Fresh reader; cache mode thêm khi cần | Chuỗi lặp theo budget đã khóa | Lõi: visibility; không là proof mọi history |
| B3 | Strict pairs; append với 2/4 writers khi concurrent write thuộc ca | Pilot rồi chốt tập run chính thức | Có điều kiện theo semantics cần dùng |
| B4 | Một fault liên quan; response-loss riêng nếu còn nguồn lực/cần | Pilot rồi chốt theo fault model | Có điều kiện; không ước lượng xác suất lỗi hiếm |
| B5 | Một cặp source–target nếu requirement cần | Dry run rồi rehearsal xác nhận | Migration, không benchmark toàn bộ 6×5 cặp |

Đây là run budget ban đầu, **không phải chứng minh đủ mẫu**. Tính cả giờ xây adapter, auth/policy, fixture/reset, oracle, điều tra failure, phân tích và thời gian reviewer; 72 phút B1 không đại diện tổng công nghiên cứu. Chọn hai cấu hình trước; ứng viên thứ ba và full fault/migration chỉ thêm nếu câu hỏi quyết định cần. Không nhân mọi cache × size × load × engine × backend thành factorial. Mọi B trong ca vẫn phải được xác minh hoặc để UNKNOWN nếu budget không đủ; việc rút scope không được biến B thành U sau khi thấy kết quả.

**Giai đoạn A — pilot/dimensioning:** kiểm tra driver, variability, warm-up và cache state, request/run dependence, timeouts và drift. Chọn cùng dải tải có ý nghĩa cho các cấu hình; nếu một cấu hình chưa đạt endpoint/contract thì xử lý feasibility trước. Số 100 bảng, 5/20/50 ops/s, 1 phút warm-up, 100 append và 3 run không có căn cứ đại diện production, chỉ là seed để kiểm tra setup. Không dùng dữ liệu đã xem để đồng thời chọn tham số và xác nhận ứng viên thắng.

**Giai đoạn B — khóa kế hoạch:** ghi primary outcome (ví dụ p95 của logical load trên cohort nào), unit, baseline, tải/quy mô, số run/ngân sách tối đa, reset, seed, thứ tự run, độ chính xác cần, failure/timeout rule và stop rule. Chọn warm-up từ pilot, giữ fixed policy trong lượt chính; nếu không đạt trạng thái ổn định thì báo transient hoặc inconclusive, không tùy ý cắt đoạn chậm. Chọn cùng timeline warm-up hợp lý cho các ứng viên hoặc công khai khác biệt và mục tiêu đo. Với phạm vi nhiều cell, chọn cell chính trước; các cell còn lại là khám phá, không chỉ báo cell có lợi nhất.

**Giai đoạn C — dữ liệu đo mới:** thực hiện kế hoạch đã khóa, xen/đảo thứ tự ứng viên trong block theo seed. Không dừng khi thấy một bên thắng hoặc thêm run chỉ cho một bên mà giấu quy tắc. Một đợt bổ sung cần amendment có lý do và được báo riêng. Dừng vì lỗi harness/môi trường phải giữ log và áp cùng quy tắc loại/rerun.

**Giai đoạn D — diễn giải:**

- Bộ tối thiểu báo từng run: goodput, số scheduled/ack/reject/unknown, p50/p95 có tên population rõ, variation và traces. Nếu tóm tắt median của p95 các run phải gọi đúng tên, không gọi là p95 gộp. Min–max run là mô tả, không là confidence interval.
- Ba run không đủ để mặc định ước lượng chính xác variance hay p95/p99. Không báo formal CI nếu chưa xác định được estimator, đơn vị resampling/correlation, sample adequacy và cách xử lý censoring. Công thức mean/execution time trong Kalibera–Jones không chuyển trực tiếp thành CI cho request-tail p95.
- Nếu ca chỉ cần minh họa phương pháp, báo chênh lệch quan sát và để khuyến nghị performance có điều kiện. Nếu cần SLO acceptance chính thức, khóa riêng estimator và quy tắc bound/error budget với người phụ trách trước đo; chưa có kế hoạch hợp lệ hoặc dữ liệu không phân biệt ngưỡng thì UNKNOWN. Không biến tất cả lần đo nằm dưới SLO thành bảo đảm production.
- Nếu có inference phù hợp, xem uncertainty của **chênh lệch/ratio tại cell đã xác định**, không chỉ nhìn hai CI biên có chồng lấn hay không. Phân biệt statistical difference với mức cải thiện có ý nghĩa thực tế.
- Báo cả failed/late/unresolved operations; không điền timeout thành latency đúng bằng deadline rồi dùng như completion thật. Data không đủ phải dẫn tới giới hạn kết luận, không dẫn tới số liệu suy đoán.

Nguyên tắc phân biệt workload/adapter kế thừa [YCSB](https://doi.org/10.1145/1807128.1807152); pilot/lặp/bất định từ [Kalibera & Jones](https://doi.org/10.1145/2464157.2464160); history và giới hạn suy correctness tham khảo [Elle](https://doi.org/10.14778/3430915.3430918); công bố cấu hình/variation từ [Hoefler & Belli](https://doi.org/10.1145/2807591.2807644). Không dùng nguyên YCSB KV hoặc Elle checker khi chưa chứng minh mapping catalog sang model của chúng.

## 6. Gắn kết quả với quyết định và chi phí

Mỗi kết quả gắn C-ID và R-ID, bao gồm phạm vi, unit, uncertainty và evidence ID. Trước benchmark viết recommendation tạm thời và câu hỏi đang thiếu; sau benchmark ghi gate nào đổi, trade-off nào rõ hơn hoặc confidence nào thay đổi. Không thay đổi khuyến nghị cũng là kết quả hợp lệ.

Ước tính chi phí ở cùng kỳ H và mức dịch vụ: `TCO(H) = triển khai + migration + chi phí hạ tầng/dịch vụ trong H + nhân công vận hành trong H + exit nếu thuộc phạm vi`. Liệt kê các hạng mục loại trừ và rủi ro chưa lượng hóa, tránh double count. Giữ giờ công riêng nếu chưa có đơn giá; thực hiện thấp/cơ sở/cao chỉ khi có căn cứ cho khoảng. Tính chênh lệch so baseline cùng scope; không gọi chênh lệch lab là tiết kiệm thực tế. Chi phí API/bytes có thể dùng usage đo từ benchmark nhưng cần workload production được xác nhận để ngoại suy.

Phiên bản v2 chỉ cho phép ba loại kết luận kinh tế: **resource ledger đo trong lab**, **ước tính kịch bản có đơn giá/giả định**, hoặc **hiệu quả quan sát thực tế có baseline**. Hiện chưa có dữ liệu cho loại nào. H không tự chọn để tạo lợi thế; managed/self-hosted phải tính cùng service envelope (HA/backup/support/on-call nếu được yêu cầu), không chỉ catalog container.

Tách active human time, machine elapsed time, thời gian học và vận hành lặp. Một lần cài nhanh/chậm của một sinh viên không ước lượng đáng tin chi phí đội production. Ghi operator/kinh nghiệm/thứ tự/rehearsal; thiếu thông tin thì giữ giờ công lab với phạm vi, không ngoại suy tháng. Mỗi task ID chỉ vào một khoản tiền. Nếu chưa có workload thật, không nhân request lab ra chi phí năm. Chênh lệch TCO dự kiến chỉ là kịch bản; chưa có adoption, mức dịch vụ và baseline quan sát thì không gọi là ROI, lợi nhuận hoặc tiết kiệm đã đạt.

## 7. Điều kiện sẵn sàng chạy và dừng

Trước khi chạy: xác nhận ca P0 hoặc thay ca; chọn 2–3 ứng viên; ghim release/image digest/client/storage/DB; điền manifest; duyệt oracle; định nghĩa acceptance thresholds nếu có; kiểm tra tài nguyên; xác định seed/reset, auth và privacy logs. Chưa đáp ứng thì chỉ hoàn thành thiết kế, không nhận benchmark reproducible đã sẵn sàng.

Dừng một cell nếu oracle tìm phản ví dụ cần điều tra, driver mất khả năng tạo tải, môi trường sai manifest hoặc budget đạt giới hạn đã định. Giữ log và trạng thái, không xóa để biến thành run thành công. Dừng toàn nghiên cứu thực nghiệm khi đã trả lời các bất định quyết định trong ngân sách, hoặc công bố những câu hỏi còn inconclusive. Không cần benchmark cả sáu catalog nếu tài liệu và yêu cầu đã loại hợp lệ; không loại vì chưa có thời gian triển khai rồi ghi sản phẩm kém.
