# Framework lựa chọn technical catalog theo yêu cầu và bằng chứng

Ngày thiết kế: **13/10/2026**. Trạng thái: **thiết kế để thực hiện; chưa chạy benchmark, chưa có số liệu kết quả, chưa có shortlist được xác nhận cho Viettel**.

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

Đây là **15 mục đánh giá vận hành hóa 8 nhóm kỹ thuật cùng 4 nhóm bổ sung**, không phải 15 trọng số. B/U/I chỉ được chốt theo hồ sơ dự án. Trong cột kiểm chứng: D=tài liệu chính thức đúng phiên bản; F=kiểm thử chức năng; P=benchmark; E=ước tính công/chi phí. Mã bài thử tham chiếu protocol.

| ID / tiêu chí | Ý nghĩa đối với quyết định | Khi là B / khi là U hoặc I | Bằng chứng cần thu thập | Kiểm chứng | Khi thiếu dữ liệu |
|---|---|---|---|---|---|
| C01 Mô hình đối tượng | Ánh xạ namespace, table, view, branch/tag và ownership vào hệ thống | B: biểu diễn được đối tượng/thao tác bắt buộc; U: giảm mapping hoặc workaround. Branch chỉ B khi có workflow cần | Sơ đồ đối tượng; naming/depth/quotas; mapping từng đối tượng; giới hạn | D + F B0 tạo/list/đổi tên/xóa đúng phạm vi | U-B cho mapping bắt buộc; đối tượng ngoài ca là U-N, không suy thiếu tính năng = kém |
| C02 Trách nhiệm metadata | Xác định ai sở hữu pointer, metadata file, lịch sử, cleanup, quyền và catalog state; tránh mất/chồng trách nhiệm | B: phân công đáp ứng lifecycle/durability yêu cầu; U: giảm công điều phối | Sơ đồ luồng; owner từng loại trạng thái; điều kiện drop/purge/GC; backup boundary | D + F B0/B4; lifecycle test bổ sung khi cần | Chưa rõ ai chịu trách nhiệm → U-B nếu ảnh hưởng dữ liệu; không suy catalog lưu mọi metadata |
| C03 API/giao thức/client | Khả năng engine gọi đúng thao tác, không chỉ có endpoint | B: đường tích hợp cần thiết được hỗ trợ; U: giảm adapter và thay đổi ứng dụng | Release docs; matrix client/API; endpoint discovery; effective config; trace và lỗi | D + F B0; P B1/B2 cho đường đã xác minh | U-B; không suy REST-compatible = mọi endpoint hoặc mọi engine hoạt động |
| C04 Xác thực | Tích hợp identity, token, TLS và vòng đời phiên | B: cơ chế và vòng đời credentials đáp ứng yêu cầu; U: giảm công cấu hình/rotation | Auth flow; issuer/audience; token expiry/refresh; TLS; log đã che secrets | D + F B0 token hợp lệ/hết hạn/sai; refresh đo riêng nếu cần | U-B; thiếu kết nối IdP không được thay bằng anonymous rồi ghi PASS |
| C05 Phân quyền và audit | Ngăn thao tác vượt quyền ở đúng boundary; truy vết chủ thể | B: action/resource/tenant bắt buộc được enforce; U: thuận tiện policy/audit | Ma trận principal–resource–action; grant/revoke; nơi enforce; audit event | D + F B0: allow/deny/list visibility/revoke theo SLA; thử fresh session lẫn cache nếu liên quan | U-B; 403 của một đường không chứng minh storage hoặc mọi engine được bảo vệ |
| C06 Commit, concurrency, consistency | Xác định atomicity/visibility, xung đột hợp lệ, retry, trạng thái không rõ | B: semantics và lỗi chấp nhận được; U: goodput/latency trong cùng semantics | Contract đúng phiên bản; transaction boundary; retry map; lịch sử request/ack; snapshot/manifest | D + F/P B2/B3/B4 với oracle định trước | U-B cho semantics; thiếu khả năng quan sát → kết luận inconclusive, không tự nhận linearizable |
| C07 Persistence và phục hồi | Biết trạng thái sống qua restart/restore, phạm vi dữ liệu có thể mất | B: durability, RTO/RPO nếu đã xác nhận; U: phục hồi đơn giản | Backend/schema; persistence/flush; backup/restore procedure; log phục hồi | D + F B4 restart; restore riêng nếu RPO/backup là B | U-B; không dùng in-memory để đại diện durable deployment; restart không chứng minh DR |
| C08 Hiệu năng và mở rộng | Đạt tải metadata và khả năng tăng tải trong ngân sách | B: SLO tại tải/quy mô xác nhận; U: dư địa, latency, chi phí tại tải đó | Request mix, cardinality/metadata bytes; latency–goodput; lỗi, backlog; CPU/RAM/DB/storage metrics | P B1/B2; scale-out là bài mở rộng độc lập | U-P nếu chưa có SLO, chỉ mô tả đường đo; nếu gần ngưỡng và sai số chưa phân biệt → U-B |
| C09 Truy cập storage | Kiểm soát đường đến object store, phạm vi credentials, signing/vending và thu hồi | B: đáp ứng mô hình tin cậy và storage bắt buộc; U: giảm secrets/công tích hợp | Access paths; IAM/bucket policy; scoped credential TTL; direct access; STS/provider dependencies | D + F B0: allowed/denied prefix, expiry, đường bypass theo quyền thực tế | U-B; static credentials trong lab không chứng minh credential vending hoặc chặn bypass |
| C10 Table format và interoperability | Đọc/ghi thực sự qua engine/format cần dùng; tránh nhầm read compatibility với native commit | B: matrix thao tác × engine × format/version; U: lựa chọn engine tương lai đã có nhu cầu | Ma trận read/append/schema/DDL; format features; snapshot/data checksums | D + F B0 round-trip; engine thứ hai chỉ bắt buộc nếu requirement cần | U-B từng ô; UniForm đọc được không tự chứng minh ghi native Iceberg |
| C11 Federation/phạm vi quản lý | Đáp ứng việc quản lý nhiều backend, nguồn hoặc domain nếu cần | B: federation là yêu cầu; U: giảm công quản lý; I/N/A nếu chỉ một catalog | Sơ đồ backend/connector; pushdown auth; consistency/sync; overhead; failure boundary | D + F bài federation; P so backend trực tiếp với tầng federation cùng backend | U-B khi cần; ngoài ca dùng U-N. Không thưởng điểm federation mặc định |
| C12 Vận hành và quan sát | Triển khai, nâng cấp, giám sát và xử lý sự cố trong năng lực đội | B: runbook/observability/support bắt buộc; U: thời gian, thao tác và phụ thuộc | Runbook; metrics/log/audit; upgrade/rollback; số dịch vụ; nhật ký giờ công | D + F B4; rehearsal deploy/upgrade; E giờ công, tách lần học đầu và lần lặp | U-P, ghi khoảng/giả định; không suy ít container = ít công vận hành |
| C13 Chi phí vòng đời | Kiểm tra ngân sách và đánh đổi giữa dịch vụ, hạ tầng, nhân công, chuyển đổi | B: trần ngân sách; U: TCO trong cùng kỳ và mức dịch vụ | Đơn giá/ngày/region; giờ tài nguyên; API/storage/network; công triển khai/vận hành/migration; baseline | E theo kịch bản, dùng usage đo được từ P; chưa có đơn giá giữ đại lượng tài nguyên/giờ công | U-B nếu cần chứng minh ngân sách; U-P cho xếp ưu tiên; không đặt OSS = 0 hoặc mặc định tiết kiệm |
| C14 Migration và exit | Chuyển catalog giữ dữ liệu/metadata/quyền và có thể rollback trong giới hạn | B: migration/downtime/rollback khi thay hệ thống; U: giảm lock-in và công chuyển | Inventory UUID/schema/snapshot/location; mapping grants; procedure; limitations; đối tượng không chuyển được | D + F B5; E giờ công/downtime; checksum và đọc sau chuyển | U-B khi migration là B; ở greenfield ghi exit risk U-P, không bịa thời gian |
| C15 Độ trưởng thành và khả năng hỗ trợ | Đánh giá rủi ro của đúng release/đường tích hợp; license và support đáp ứng tổ chức | B: license/support hoặc cấm experimental nếu được yêu cầu; U: release practice, maintenance, upgrade evidence | Release notes/support matrix; trạng thái feature; issue liên quan; upgrade docs; license; phương án hỗ trợ | D đúng ngày/release + F smoke/upgrade nếu cần; không benchmark độ trưởng thành | U-B với yêu cầu bắt buộc; còn lại U-P. Không lấy GitHub stars/tuổi dự án làm đại diện duy nhất |

## 5. Mức độ chắc chắn của kết luận

Không xuất phần trăm confidence tự đặt hoặc lấy trung bình điểm bằng chứng. Ghi **hai trục độc lập**:

1. **Độ vững của bằng chứng cho từng mệnh đề:**
   - E0: chưa có hoặc mâu thuẫn chưa giải quyết.
   - E1: tài liệu đúng phạm vi nhưng chưa thử hành vi quan trọng; hoặc ước tính có giả định.
   - E2: kiểm thử/đo có protocol, raw evidence, cấu hình rõ trong lab; bất định được báo.
   - E3: kết quả quan trọng được lặp/tái kiểm tra và phạm vi tương ứng yêu cầu đã được xác nhận. Không đồng nghĩa đúng phổ quát.
   - Mức bằng chứng thích hợp phụ thuộc mệnh đề: license có thể xác minh bằng tài liệu; benchmark không thay chứng cứ license. E-label không phải bảng xếp hạng mọi loại nguồn.
2. **Độ bền của khuyến nghị:** giữ nguyên / đổi trong một số kịch bản hợp lý / chưa xác định, kèm các ngưỡng làm đổi quyết định.

Nhãn khuyến nghị:

| Nhãn | Điều kiện sử dụng |
|---|---|
| Chưa kết luận | Còn B=UNKNOWN ảnh hưởng phương án được khuyến nghị, hoặc chưa đủ dữ liệu/sở thích để phân biệt |
| Có điều kiện | Các B đạt mức bằng chứng đã thống nhất trong phạm vi ca; khuyến nghị phụ thuộc các giả định/ước tính còn rõ ràng |
| Vững trong phạm vi đã thử | Các B quan trọng có bằng chứng phù hợp; hiệu năng đạt theo quy tắc bất định; ưu tiên được xác nhận; khuyến nghị giữ trong các kịch bản độ nhạy đã xét |

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

Phần bắt buộc cho ca Iceberg self-hosted đề xuất: hồ sơ yêu cầu, 15 mục rà soát, B0–B4 cho hai ứng viên (B4 giới hạn restart), ước tính chi phí theo khoảng, decision record và sensitivity. B5 trở thành bắt buộc nếu migration là B; federation, branch/multi-table, backup restore/HA hoặc engine thứ hai trở thành bắt buộc khi yêu cầu tương ứng có trong ca. Ứng viên thứ ba và scale-out là mở rộng nếu không được yêu cầu.

## 7. Kế thừa và giới hạn

Kế thừa quy trình theo yêu cầu/assessment từ [Bjarnason et al. 2023](https://doi.org/10.1007/s10664-023-10288-w); feasibility và vai trò kiểm tra bổ sung từ [Farshidi et al. 2018](https://doi.org/10.1080/12460125.2018.1464821); scenario/risk từ [ATAM](https://www.sei.cmu.edu/library/atam-method-for-architecture-evaluation/); chọn cách tổng hợp theo bối cảnh từ [Roy & Słowiński 2013](https://doi.org/10.1007/s40070-013-0004-7). Không kế thừa nguyên bộ tiêu chí DBMS, không nhận đây là ATAM đầy đủ.

Mã tiêu chí, trạng thái, confidence rubric và protocol catalog là **điều chỉnh đề xuất**, chưa có validation độc lập. Không khẳng định tính mới từ việc chưa tìm thấy nghiên cứu tương tự. Không dùng tỷ trọng chấm cuộc thi 30/20/20/30 làm trọng số chọn catalog. Hiệu quả kinh tế thực phải có baseline và chi phí thực; tính ứng dụng cần hồ sơ ca được xác nhận; tính hoàn thiện có thể chứng minh bằng khả năng truy vết và tái lập.
