# Framework lựa chọn technical catalog theo yêu cầu và bằng chứng

Phiên bản **v2, sửa sau thẩm định ngày 13/10/2026**. Trạng thái: **thiết kế, chưa validation thực nghiệm; chưa chạy benchmark, chưa có số liệu kết quả hoặc shortlist được xác nhận cho Viettel**. [Báo cáo thẩm định và vị trí bản gốc](review-2026-10-13/review.md); [kiểm tra nguồn](review-2026-10-13/source-audit.md). Bản v1 được lưu để đối chiếu, không phải protocol đang có hiệu lực.

Phạm vi khảo sát tài liệu: Hive Metastore, AWS Glue Data Catalog, Apache Polaris, Project Nessie, Apache Gravitino, Unity Catalog OSS. Enterprise/business catalog chỉ là bối cảnh. Phương pháp chính: lọc điều kiện bắt buộc → phân tích kịch bản và đánh đổi → khuyến nghị có điều kiện → kiểm tra độ nhạy. Không yêu cầu mọi tiêu chí trở thành điểm số.

## 1. Bộ tài liệu và ranh giới bằng chứng

- Tài liệu này: đầu vào, tiêu chí, quy tắc xử lý và đầu ra.
- [Protocol benchmark tối thiểu](benchmark-protocol.md): cấu hình P0 đề xuất, kịch bản và kiểm soát nhiễu.
- [Biểu mẫu thực hiện](templates.md): yêu cầu, phương án, bằng chứng, run và quyết định; các ô kết quả đều để trống.
- [Tổng quan nguồn đã đọc](../catalog-method-review/README.md): phạm vi đọc và hạn chế từng nguồn.

**Đã có từ người dùng:** đề tài, sáu công nghệ, tám nhóm kỹ thuật, mục tiêu chọn theo yêu cầu, kết hợp tài liệu và thực nghiệm. **Đề xuất của người thiết kế:** các quy tắc, mã tiêu chí, confidence rubric, profile lab và workload dưới đây. **Chưa biết:** yêu cầu thực tế, ngưỡng, SLA, lab, phiên bản sẽ chạy, mức chấp nhận công nghệ experimental, nguồn chi phí và baseline của Viettel. Số tham số lab là đầu vào thiết kế minh họa, không phải nhu cầu dự án hoặc kết quả đo.

## 2. Đầu vào tối thiểu

| Nhóm | Thông tin phải ghi | Khi chưa có |
|---|---|---|
| Mục tiêu quyết định | Xây mới/thay thế; đối tượng sử dụng; thời hạn; người xác nhận; cần shortlist hay quyết định triển khai | Chỉ lập ca nghiên cứu giả định và khuyến nghị nghiên cứu |
| Tích hợp | Engine/client, phiên bản, table format/version, storage, đường API; thao tác cần đọc/ghi | Chưa xác nhận tương thích bằng nhãn sản phẩm |
| Tải metadata | Số namespace/bảng; kích thước metadata/snapshot; tần suất load/list/commit; concurrency; hot tables | Dùng P0 để kiểm tra phương pháp, không kết luận đáp ứng production |
| Ràng buộc | Hạ tầng, vị trí dữ liệu, danh tính, phân quyền, yêu cầu storage, ngân sách, RTO/RPO, hỗ trợ | Gắn người chịu trách nhiệm và thời điểm xác nhận; không tự chọn ngưỡng |
| Sở thích | Mục tiêu có thể đánh đổi; mức cải thiện có ý nghĩa; thứ tự ưu tiên; chấp nhận rủi ro | Có thể giữ shortlist thay vì ép chọn một phương án |
| Vòng đời | Hệ thống hiện tại, migration, rollback/exit, nhân sự vận hành, kỳ tính chi phí | Phân tích kịch bản và khoảng ước tính; chưa khẳng định tiết kiệm |

Một yêu cầu có thể sinh nhiều tiêu chí. Một tiêu chí có thể có **mức tối thiểu bắt buộc** và **mục tiêu cải thiện** riêng. Ví dụ latency chỉ là gate khi đã có ngưỡng và workload được xác nhận; nhanh hơn dưới ngưỡng chỉ có giá trị nếu người quyết định thực sự cần.

### 2.1 Hợp đồng quyết định phải điền trước shortlist

Ghi một câu hỏi quyết định cụ thể; mục tiêu xây mới/thay thế; người sử dụng kết quả; trạng thái ca thực/ca giả định; tập chức năng và mức dịch vụ tối thiểu; những đánh đổi còn mở. Mỗi B phải có **nguồn và lý do không thể đánh đổi**, trạng thái xác nhận và hậu quả nếu không đạt. Yêu cầu giả định chỉ tạo kết luận cho ca giả định. Không có yêu cầu được xác định không đồng nghĩa mọi cấu hình tự động PASS.

Ngưỡng acceptance lấy từ yêu cầu hoặc dẫn xuất có lập luận được người phụ trách xác nhận. Tham số pilot như 100 bảng/3 run không phải ngưỡng acceptance. Không có ngưỡng thì chỉ báo quan sát. Ưu tiên theo thứ tự cũng là một mô hình sở thích: phải nêu các chiều bị hy sinh và trường hợp đổi ưu tiên, dù không có trọng số số học.

Rà cả sáu catalog theo cùng chuẩn bằng chứng. Tách **đủ điều kiện chức năng**, **được chọn vào mẫu nghiên cứu**, **có thể triển khai trong lab**. Giới hạn thời gian làm một ứng viên không được đo không phải bằng chứng nó không phù hợp. Vai trò Polaris trong tên đề tài giải thích việc phân tích sâu, không tự chứng minh nó vào shortlist dự án.

## 3. Quy tắc đánh giá

### 3.1 Đơn vị đánh giá

`phương án = catalog + release/digest + API + backend/persistence + engine/client + format + storage + auth/policy + tài nguyên + cấu hình`.

Mỗi thay đổi có thể ảnh hưởng kết luận tạo một revision phương án. Ghi riêng dịch vụ phụ thuộc (IdP, Ranger, STS, proxy, DB). Không so một catalog standalone với một hệ thống có thêm federation/auth service rồi quy toàn bộ chênh lệch cho nhãn sản phẩm.

### 3.2 Kiểu tiêu chí và trạng thái

- **B — bắt buộc:** điều kiện tuyệt đối được chủ yêu cầu xác nhận; không bù bằng lợi ích khác.
- **U — ưu tiên:** dùng phân tích đánh đổi; giữ đơn vị gốc hoặc diễn giải định tính có căn cứ.
- **I — thông tin:** giải thích kiến trúc/rủi ro; chưa trực tiếp loại hoặc ưu tiên.
- Kết quả từng điều kiện: **PASS**, **FAIL**, **UNKNOWN**, **N/A**. N/A cần lý do xác nhận ngoài phạm vi; không dùng để che thiếu hỗ trợ cần thiết.
- PASS nghĩa là đạt yêu cầu **ở mức bằng chứng và phạm vi đã quy định**, không phải bảo đảm hệ thống luôn đúng.

### 3.3 Tạo shortlist

1. Ghi nguồn, phiên bản yêu cầu, ngưỡng và loại bằng chứng đủ chấp nhận **trước** khi nhìn kết quả.
2. Bất kỳ B=FAIL nào: loại cấu hình đang xét, ghi phản ví dụ hoặc nguồn. Cấu hình thay thế cần đánh giá lại.
3. Có B=UNKNOWN, chưa có B=FAIL: giữ trong danh sách **cần xác minh**; không ghi là đủ điều kiện triển khai.
4. Mọi B=PASS: vào danh sách **đủ điều kiện trong phạm vi đánh giá**. Có thể có shortlist tài liệu để vào lab trước; nhãn này khác shortlist sau kiểm thử.
5. So sánh các U liên quan. Chỉ loại vì Pareto khi mọi chiều liên quan đủ bằng chứng so sánh; chiều định tính không có thứ tự và khoảng chưa phân biệt được thì không ép quan hệ trội.
6. Áp dụng quy tắc ưu tiên đã xác nhận: ví dụ đạt SLO và trong ngân sách rồi giảm công vận hành. Ghi mức đánh đổi chấp nhận được; không tự phát minh thứ tự ưu tiên sau khi thấy phương án yêu thích.
7. Nếu chưa đủ ưu tiên: giữ nhiều phương án, nêu câu hỏi nào sẽ phân biệt chúng. Không dùng số lượng tính năng làm tie-break mặc định.
8. Kiểm tra độ nhạy với khoảng tải, chi phí, ngưỡng và sở thích hợp lý; ghi các điểm làm đổi shortlist/khuyến nghị. Không giả định phân phối xác suất khi không có dữ liệu.

### 3.4 Quy tắc thiếu dữ liệu dùng chung

- **U-B:** thiếu bằng chứng cho B → UNKNOWN, ưu tiên xác minh; chưa khuyến nghị triển khai.
- **U-P:** thiếu dữ liệu cho U → để trống, dùng khoảng có nguồn hoặc các kịch bản; không gán 0, trung bình hoặc điểm phạt tùy ý. Nếu khoảng có thể đổi quyết định, cần đo thêm hoặc giảm độ chắc chắn.
- **U-C:** tài liệu mâu thuẫn, khác phiên bản hoặc khác deployment → tách cấu hình, giữ cả nguồn và mở kiểm thử phân giải.
- **U-N:** thiếu vì ngoài phạm vi thật sự → N/A với người xác nhận và lý do; không tính như ưu thế hoặc bất lợi.

## 4. Danh mục tiêu chí có thể thực hiện

Đây là **15 nhóm rà soát** từ 8 nhóm kỹ thuật và 4 nhóm bổ sung, chưa phải 15 tiêu chí nguyên tử độc lập hoặc một danh mục được chứng minh đầy đủ. Mỗi ca chọn các yêu cầu liên quan và tạo assessment row có một kết quả quan sát cụ thể; không cần điền chi tiết mọi đặc tính không ảnh hưởng quyết định. B/U/I chỉ chốt theo hồ sơ dự án. D=tài liệu đúng phiên bản; F=kiểm thử chức năng; P=benchmark; E=ước tính công/chi phí. Mã bài thử tham chiếu protocol.

| ID / tiêu chí | Ý nghĩa đối với quyết định | Khi là B / khi là U hoặc I | Bằng chứng cần thu thập | Kiểm chứng | Khi thiếu dữ liệu |
|---|---|---|---|---|---|
| C01 Mô hình đối tượng | Ánh xạ namespace, table, view, branch/tag và ownership vào hệ thống | B: biểu diễn được đối tượng/thao tác bắt buộc; U: giảm mapping hoặc workaround. Branch chỉ B khi có workflow cần | Sơ đồ đối tượng; naming/depth/quotas; mapping từng đối tượng; giới hạn | D + F B0 tạo/list/đổi tên/xóa đúng phạm vi | U-B cho mapping bắt buộc; đối tượng ngoài ca là U-N, không suy thiếu tính năng = kém |
| C02 Trách nhiệm metadata | Xác định ai sở hữu pointer, metadata file, lịch sử, cleanup, quyền và catalog state; tránh mất/chồng trách nhiệm | B: phân công đáp ứng lifecycle/durability yêu cầu; U: giảm công điều phối | Sơ đồ luồng; owner từng loại trạng thái; điều kiện drop/purge/GC; backup boundary | D + F B0/B4; lifecycle test bổ sung khi cần | Chưa rõ ai chịu trách nhiệm → U-B nếu ảnh hưởng dữ liệu; không suy catalog lưu mọi metadata |
| C03 API/giao thức/client | Khả năng engine gọi đúng thao tác, không chỉ có endpoint | B: đường tích hợp cần thiết được hỗ trợ; U: giảm adapter và thay đổi ứng dụng | Release docs; matrix client/API; endpoint discovery; effective config; trace và lỗi | D + F B0; P B1/B2 cho đường đã xác minh | U-B; không suy REST-compatible = mọi endpoint hoặc mọi engine hoạt động |
| C04 Xác thực | Tích hợp identity, token, TLS và vòng đời phiên | B: cơ chế và vòng đời credentials đáp ứng yêu cầu; U: giảm công cấu hình/rotation | Auth flow; issuer/audience; token expiry/refresh; TLS; log đã che secrets | D + F B0 token hợp lệ/hết hạn/sai; refresh đo riêng nếu cần | U-B; thiếu kết nối IdP không được thay bằng anonymous rồi ghi PASS |
| C05 Phân quyền và audit | Ngăn thao tác vượt quyền ở đúng boundary; truy vết chủ thể | B: action/resource/tenant bắt buộc được enforce; U: thuận tiện policy/audit | Ma trận principal–resource–action; grant/revoke; nơi enforce; audit event | D + F B0: allow/deny/list visibility/revoke theo SLA; thử fresh session lẫn cache nếu liên quan | U-B; 403 của một đường không chứng minh storage hoặc mọi engine được bảo vệ |
| C06 Commit, concurrency, consistency | Xác định atomicity/visibility, xung đột hợp lệ, retry, trạng thái không rõ | B: semantics và lỗi chấp nhận được; U: goodput/latency trong cùng semantics | Contract đúng phiên bản; transaction boundary; retry map; lịch sử request/ack; snapshot/manifest | D + F/P B1V/B2/B3/B4 theo hợp đồng và fault model cần kiểm tra | U-B cho semantics; thiếu khả năng quan sát → kết luận inconclusive, không tự nhận linearizable |
| C07 Persistence và phục hồi | Biết trạng thái sống qua restart/restore, phạm vi dữ liệu có thể mất | B: durability, RTO/RPO nếu đã xác nhận; U: phục hồi đơn giản | Backend/schema; persistence/flush; backup/restore procedure; log phục hồi | D + F B4 restart; restore riêng nếu RPO/backup là B | U-B; không dùng in-memory để đại diện durable deployment; restart không chứng minh DR |
| C08 Hiệu năng và mở rộng | Đạt tải metadata và khả năng tăng tải trong ngân sách | B: SLO tại tải/quy mô xác nhận; U: dư địa, latency, chi phí tại tải đó | Request mix, cardinality/metadata bytes; latency–goodput; lỗi, backlog; CPU/RAM/DB/storage metrics | P B1/B2; scale-out là bài mở rộng độc lập | U-P nếu chưa có SLO, chỉ mô tả đường đo; nếu gần ngưỡng và sai số chưa phân biệt → U-B |
| C09 Truy cập storage | Kiểm soát đường đến object store, phạm vi credentials, signing/vending và thu hồi | B: đáp ứng mô hình tin cậy và storage bắt buộc; U: giảm secrets/công tích hợp | Access paths; IAM/bucket policy; scoped credential TTL; direct access; STS/provider dependencies | D + F B0: allowed/denied prefix, expiry, đường bypass theo quyền thực tế | U-B; static credentials trong lab không chứng minh credential vending hoặc chặn bypass |
| C10 Table format và interoperability | Đọc/ghi thực sự qua engine/format cần dùng; tránh nhầm read compatibility với native commit | B: matrix thao tác × engine × format/version; U: lựa chọn engine tương lai đã có nhu cầu | Ma trận read/append/schema/DDL; format features; snapshot/data checksums | D + F B0 round-trip; engine thứ hai chỉ bắt buộc nếu requirement cần | U-B từng ô; UniForm đọc được không tự chứng minh ghi native Iceberg |
| C11 Federation/phạm vi quản lý | Đáp ứng việc quản lý nhiều backend, nguồn hoặc domain nếu cần | B: federation là yêu cầu; U: giảm công quản lý; I/N/A nếu chỉ một catalog | Sơ đồ backend/connector; pushdown auth; consistency/sync; overhead; failure boundary | D + F bài federation; P so backend trực tiếp với tầng federation cùng backend | U-B khi cần; ngoài ca dùng U-N. Không thưởng điểm federation mặc định |
| C12 Vận hành và quan sát | Triển khai, nâng cấp, giám sát và xử lý sự cố trong năng lực đội | B: runbook/observability/support bắt buộc; U: thời gian, thao tác và phụ thuộc | Runbook; metrics/log/audit; upgrade/rollback; số dịch vụ; nhật ký giờ công | D + F B4; rehearsal deploy/upgrade; E giờ công, tách lần học đầu và lần lặp | U-P, ghi khoảng/giả định; không suy ít container = ít công vận hành |
| C13 Chi phí vòng đời | Kiểm tra ngân sách và đánh đổi giữa dịch vụ, hạ tầng, nhân công, chuyển đổi | B: trần ngân sách; U: TCO trong cùng kỳ và mức dịch vụ | Đơn giá/ngày/region; giờ tài nguyên; API/storage/network; công triển khai/vận hành/migration; baseline | E theo kịch bản, dùng usage đo được từ P; chưa có đơn giá giữ đại lượng tài nguyên/giờ công | U-B nếu cần chứng minh ngân sách; U-P cho xếp ưu tiên; không đặt OSS = 0 hoặc mặc định tiết kiệm |
| C14 Migration và exit | Chuyển catalog giữ dữ liệu/metadata/quyền và có thể rollback trong giới hạn | B: migration/downtime/rollback khi thay hệ thống; U: giảm lock-in và công chuyển | Inventory UUID/schema/snapshot/location; mapping grants; procedure; limitations; đối tượng không chuyển được | D + F B5; E giờ công/downtime; checksum và đọc sau chuyển | U-B khi migration là B; ở greenfield ghi exit risk U-P, không bịa thời gian |
| C15 Độ trưởng thành và khả năng hỗ trợ | Đánh giá rủi ro của đúng release/đường tích hợp; license và support đáp ứng tổ chức | B: license/support hoặc cấm experimental nếu được yêu cầu; U: release practice, maintenance, upgrade evidence | Release notes/support matrix; trạng thái feature; issue liên quan; upgrade docs; license; phương án hỗ trợ | D đúng ngày/release + F smoke/upgrade nếu cần; không benchmark độ trưởng thành | U-B với yêu cầu bắt buộc; còn lại U-P. Không lấy GitHub stars/tuổi dự án làm đại diện duy nhất |

### 4.1 Một lợi ích có một nơi đánh giá chính

| Các nhóm giao nhau | Phân công để tránh đếm lặp |
|---|---|
| C01/C03/C10 | C01 mô tả đối tượng; C03 mô tả đường API; kết quả engine thực hiện được thao tác format ghi một lần tại C10, với C01/C03 là liên kết giải thích |
| C02/C07/C12 | C02 sơ đồ owner/lifecycle; C07 đo durability/recovery theo fault; C12 đo công thao tác. Cùng một lần phục hồi có thể cung cấp dữ liệu khác đơn vị, không được kể là ba lợi ích độc lập |
| C04/C05/C09 | C04 identity; C05 quyết định quyền trên metadata/API; C09 quyền object store. Ghi một đường truy cập và điểm enforce cho từng test; API deny không thay storage deny |
| C06/C08 | C06 kết quả hợp đồng commit/visibility; mọi latency/goodput đặt ở C08, không cộng ưu thế hiệu năng lần hai tại C06 |
| C12/C13/C14 | Nhật ký công việc có task ID duy nhất. C12/C14 mô tả công/rủi ro; C13 dùng lại giờ công để tính tiền. Nếu tiền nhân công đã nằm trong TCO, chỉ giữ giờ công như chiều ưu tiên riêng khi có lý do như thiếu nhân lực, và công khai sự phụ thuộc |
| C12/C15 | C12 khả năng vận hành tại đội hiện có; C15 hỗ trợ/release lifecycle của nhà cung cấp/dự án; không suy từ số người dùng hoặc độ phổ biến |

Mỗi outcome row có `primary_C_ID`, `related_C_IDs`, metric/unit hoặc quy tắc định tính, evidence IDs và dependency notes. Không dùng số nhóm thuận lợi làm lý do thắng. Pareto không yêu cầu độc lập sở thích như mô hình cộng, nhưng cần các chiều so sánh hợp lệ; không ép thứ tự cho rủi ro định tính chưa được xác nhận.

### 4.2 Khoảng bao phủ cần hỏi thêm, không tự biến thành bắt buộc

- **Freshness/read-after-write** tại C06: client khác đọc thấy phiên bản nào, qua cache nào, sau bao lâu? B1V kiểm tra riêng; final state không trả lời câu hỏi này.
- **Đồng tồn tại nhiều tenant/noisy neighbor** tại C05/C08: tên/metadata/policy có bị lộ chéo, có quota/admission control và cách ly tài nguyên cần thiết không? Chỉ thêm test hỗn hợp nếu ca cần; không suy từ test một tenant.
- **Bảo vệ metadata và vòng đời bảo mật** tại C04/C07/C15: at-rest encryption, secrets, patch/upgrade và yêu cầu lưu trú dữ liệu nếu tổ chức yêu cầu. Đây là câu hỏi coverage, không phải kết luận Viettel có những ràng buộc cụ thể.
- **DDL đồng thời/lifecycle** tại C01/C02/C06: rename/drop/recreate, schema evolution, GC/expiry nếu có trong workflow. Append-only không chứng minh các hợp đồng này.

Nếu chức năng riêng như branch/federation/multi-table quyết định lợi ích, phải có capability scenario riêng trước khuyến nghị. Bài common REST core chỉ cung cấp bằng chứng cho giao phần chức năng, không đại diện toàn bộ giá trị sản phẩm.

## 5. Mức độ chắc chắn của kết luận

**Bỏ thang E0–E3 của v1** vì nó trộn loại nguồn, replication và độ phù hợp thành một thứ tự chưa được kiểm chứng. Không xuất phần trăm confidence hoặc tính trung bình bằng chứng. Ghi một hồ sơ cho mỗi claim:

- Loại nguồn D/F/P/E và release/đường tích hợp được bao phủ.
- Mức khớp với ca: trực tiếp / tương tự / chưa xác định, kèm lý do.
- Tình trạng kiểm chứng: tài liệu / quan sát lab / đã lặp / reviewer kiểm tra; không mặc định loại sau luôn mạnh hơn loại trước (ví dụ license).
- Phép kiểm tra có thể phát hiện gì và chưa phát hiện gì; lỗi harness/nguồn mâu thuẫn đã được phân giải chưa.
- Bất định định lượng nếu ước lượng hợp lệ; nếu chưa có thì ghi chưa ước lượng, không ghi bằng 0.
- **Độ bền của khuyến nghị** riêng: giữ nguyên / đổi / chưa xác định trên những kịch bản cụ thể đã xét. Không khái quát ra mọi yêu cầu hợp lý chưa xét.

Nhãn khuyến nghị:

| Nhãn | Điều kiện sử dụng |
|---|---|
| Chưa kết luận | Còn B=UNKNOWN ảnh hưởng phương án được khuyến nghị, hoặc chưa đủ dữ liệu/sở thích để phân biệt |
| Có điều kiện | Các B đạt mức bằng chứng đã thống nhất trong phạm vi ca; khuyến nghị phụ thuộc các giả định/ước tính còn rõ ràng |
| Có bằng chứng trực tiếp và ổn định trong các kịch bản đã xét | Các B quan trọng có bằng chứng phù hợp; hiệu năng được đọc theo kế hoạch phân tích đã khóa; ưu tiên được xác nhận; liệt kê rõ các biến thể đã xét. Đây là nhãn mô tả, không phải mức confidence thống kê |

Không nâng confidence chỉ vì phương án thắng xa trên một chỉ số. Một unknown quyết định ở yêu cầu bắt buộc vẫn chặn khuyến nghị triển khai. Confidence về thao tác load không truyền sang concurrency hay phục hồi.

## 6. Đầu ra và điều kiện hoàn thành

Một decision record phải chứa: hồ sơ yêu cầu và revision; danh sách cấu hình đủ điều kiện; danh sách loại và lý do; danh sách chờ xác minh; khuyến nghị; đánh đổi; evidence IDs; giới hạn; độ chắc chắn; các điều kiện làm đổi khuyến nghị; việc còn thiếu có người phụ trách.

| Giai đoạn | Đầu ra | Điều kiện hoàn thành |
|---|---|---|
| Đặc tả | Requirements + stakeholder + giả định | Mỗi B có nguồn, phạm vi, điều kiện kiểm tra và mức bằng chứng; nếu dùng ca giả định phải ghi nhãn |
| Sàng lọc tài liệu | Ma trận 6 catalog theo cấu hình và evidence | Phân biệt FAIL/UNKNOWN; chọn 2–3 phương án vào lab vì nhu cầu, không vì muốn sản phẩm nào thắng |
| Khóa protocol | Manifest, oracle, workload, run matrix và quy tắc đọc số liệu | Không còn TBD ảnh hưởng validity; B0 và pilot sau này quyết định readiness, chưa có ở bước thiết kế |
| Thực nghiệm (chưa thực hiện) | Raw logs, metrics, checks, run manifests | Không bỏ lỗi; đáp ứng độ chính xác đã định hoặc công bố inconclusive; chỉ các bài liên quan được chạy |
| Ra quyết định | Shortlist, recommendation, trade-off và confidence | Truy vết mọi kết luận; kiểm tra ít nhất một biến thể yêu cầu và bất định quan trọng; reviewer có thể tái dựng |

Phần lõi v2: hồ sơ ca; rà 15 nhóm ở mức checklist; assessment rows chỉ cho outcomes liên quan; hai cấu hình đã qua kiểm tra tính so sánh được; B0, B1 ở tải/quy mô liên quan, B2 và B1V; decision record, chi phí hoặc các quantities chưa quy tiền, sensitivity. B3 trở thành lõi khi concurrent writers là yêu cầu; B4/B5 và các capability test chỉ bắt buộc khi recovery/migration/chức năng tương ứng là yêu cầu. Chưa có workload thật thì đây là ca minh họa phương pháp, không là lựa chọn production. Ứng viên thứ ba chỉ thêm nếu phân biệt được một đánh đổi quan trọng trong budget.

### 6.1 Kiểm chứng chính phương pháp lựa chọn

Benchmark đúng mới kiểm chứng một phần các cấu hình. Để đánh giá tính hữu ích của framework, thêm một ca có yêu cầu được xác nhận và một biến thể, dùng cùng evidence pack cho reviewer tái dựng quyết định. Ghi số kết luận không truy được về evidence, bất đồng phân loại B/U, thời gian hoàn thành và các quyết định thay đổi sau khi bổ sung bằng chứng. Không coi đồng thuận là bằng chứng tối ưu.

Thử các tình huống logic có đáp án theo quy tắc: một B=FAIL không được vào danh sách đủ điều kiện; B=UNKNOWN không được thành PASS; outcome bị lặp không tạo lợi ích mới; đổi source version phải hủy kết luận không còn áp dụng. Đây là kiểm tra quy trình trên dữ liệu thử có nhãn, chưa được thực hiện và không phải số liệu benchmark.

Nếu muốn tuyên bố framework tốt hơn bảng so sánh thông thường, cần baseline dùng cùng yêu cầu/bằng chứng và kiểm soát thứ tự/hiệu ứng học của người đánh giá. Với một sinh viên/mentor, chỉ báo case study và giới hạn, không tuyên bố hiệu quả nhân quả hay khái quát cho Viettel.

## 7. Kế thừa và giới hạn

Kế thừa quy trình theo yêu cầu/assessment từ [Bjarnason et al. 2023](https://doi.org/10.1007/s10664-023-10288-w); feasibility và vai trò kiểm tra bổ sung từ [Farshidi et al. 2018](https://doi.org/10.1080/12460125.2018.1464821); scenario/risk từ [ATAM](https://www.sei.cmu.edu/library/atam-method-for-architecture-evaluation/); chọn cách tổng hợp theo bối cảnh từ [Roy & Słowiński 2013](https://doi.org/10.1007/s40070-013-0004-7). Không kế thừa nguyên bộ tiêu chí DBMS, không nhận đây là ATAM đầy đủ.

Mã tiêu chí, trạng thái, confidence rubric và protocol catalog là **điều chỉnh đề xuất**, chưa có validation độc lập. Không khẳng định tính mới từ việc chưa tìm thấy nghiên cứu tương tự. Không dùng tỷ trọng chấm cuộc thi 30/20/20/30 làm trọng số chọn catalog. Hiệu quả kinh tế thực phải có baseline và chi phí thực; tính ứng dụng cần hồ sơ ca được xác nhận; tính hoàn thiện có thể chứng minh bằng khả năng truy vết và tái lập.
