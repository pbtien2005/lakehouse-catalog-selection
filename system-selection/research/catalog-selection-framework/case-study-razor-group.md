# Áp dụng thử phương pháp lựa chọn catalog: Razor Group

Ngày khảo sát tài liệu: **13/10/2026**. Phương pháp tham chiếu: [framework v2](README.md) và [chương phương pháp](chuong-phuong-phap-lua-chon-catalog.md).

**Trạng thái thực hiện:** đã tìm nguồn, tái dựng bài toán, ánh xạ tiêu chí, sàng lọc tài liệu và lập khuyến nghị nghiên cứu. Chưa truy cập hệ thống của doanh nghiệp, triển khai AWS, kiểm thử chức năng hoặc chạy benchmark. Đây là áp dụng trên tài liệu công khai, chưa phải validation thực nghiệm của framework.

## 1. Hệ thống thực tế và bằng chứng công khai

AWS công bố ca Razor Group ngày 28/8/2026. Stack được mô tả gồm Spark, Iceberg trên S3 Tables, Glue Data Catalog, Lake Formation và Redshift Serverless. Bài viết nêu mục tiêu dùng chung dữ liệu giữa các engine và giảm công bảo trì bảng. Đây là mô tả triển khai của doanh nghiệp trên blog AWS, không phải bộ dữ liệu benchmark độc lập. [S1: ca Razor Group](https://aws.amazon.com/blogs/big-data/razor-groups-journey-to-a-modern-data-lakehouse-on-aws/).

Hệ thống có tài liệu công khai; không có bằng chứng cho thấy tài khoản, dữ liệu hoặc môi trường production được mở để người ngoài chạy thử. Không dùng bài hướng dẫn dựng demo làm bằng chứng rằng đã kiểm tra production.

## 2. Câu hỏi quyết định và giả định nghiên cứu

**Câu hỏi đề xuất:** nếu đánh giá lớp catalog cho kiến trúc đã công bố, nên giữ cách truy cập metadata hiện có hay bổ sung/thay đổi một catalog khác? Phương án mới cần chứng minh lợi ích gì để việc thay đổi có căn cứ?

Đây là câu hỏi do người nghiên cứu đặt ra để thực hành phương pháp, **không phải yêu cầu Razor Group đang tuyển chọn hoặc muốn thay catalog**. Kiến trúc đã được chọn trong nguồn chỉ là baseline. Không sử dụng việc họ đã chọn Glue làm bằng chứng Glue là phương án tối ưu.

Hai giả định được đặt trước khi sàng lọc:

- **A01 — phạm vi thay đổi hạn chế:** vòng đánh giá đầu giữ các engine, S3 Tables và Lake Formation trong kiến trúc đã công bố. Đây là giới hạn ca nghiên cứu, không phải ràng buộc vĩnh viễn của doanh nghiệp.
- **A02 — ưu tiên hạn chế thay đổi khi chưa chứng minh lợi ích:** chưa đề xuất migration production chỉ dựa trên khả năng có thêm tính năng. Đây là mô hình sở thích của ca nghiên cứu, chưa được doanh nghiệp xác nhận.

Nếu bỏ A01, phải mở bài toán thành thay đổi cả storage/table service, quyền và công vận hành. Khi đó không thể gọi kết quả là so sánh riêng lớp catalog.

## 3. Từ bối cảnh thành tiêu chí cần kiểm tra

Các B dưới đây là **điều kiện bắt buộc được người nghiên cứu dẫn xuất cho ca A01**, chưa phải bộ acceptance criteria được Razor Group phê duyệt. Các chi tiết thao tác và mức dịch vụ vẫn cần xác nhận.

| Mã yêu cầu | Điều kiện của ca nghiên cứu | Nhóm tiêu chí | Phân loại | Bằng chứng đủ để kết luận và nội dung chưa biết |
|---|---|---|---|---|
| R01 | Đường truy cập mới phải giữ workflow Spark ghi và engine phục vụ đọc trên cùng tập bảng, không tạo catalog state phân kỳ | C02, C03, C06, C10 | B theo A01 | Tài liệu chỉ định đường tích hợp là bước sàng lọc. Cần test với đúng phiên bản Spark/Redshift, cùng table identity và snapshot/marker. Bộ phiên bản production chưa có |
| R02 | Không làm mất các chính sách truy cập cần bảo toàn | C04, C05, C09 | B theo A01 | Cần ma trận principal–action–resource và các filter thực dùng; test allow/deny/revoke qua từng engine và đường storage. Không tự đặt row filter là B cho mọi đường ghi |
| R03 | Tương thích với backend bảng đang giữ trong ca A01 | C01, C02, C03, C11 | B theo A01 | Cần mapping đối tượng và một đường tích hợp xác định tới S3 Tables; dùng được S3 thường chưa trả lời điều kiện này |
| R04 | Giữ đúng hợp đồng commit/visibility mà workload yêu cầu | C06, C07 | B trong ca đọc/ghi | Cần xác định semantics, retry, lỗi không rõ kết quả và giới hạn actor; kiểm thử history. Contract cụ thể và các yêu cầu lỗi chưa công khai đầy đủ |
| R05 | Đạt mức dịch vụ metadata tại workload liên quan | C08 | Chưa thể chốt B/U | Không có metadata QPS, SLO, cardinality và phân bố request đủ dùng. Chưa đặt ngưỡng hoặc quy đổi API nghiệp vụ thành metadata QPS |
| R06 | Giảm công vận hành và công bảo trì thuộc phạm vi phương án | C12, C13 | U | Cần ledger công việc, service boundaries và thời gian lặp. Đếm riêng công vận hành catalog với công maintenance bảng |
| R07 | Có lợi ích đủ bù công tích hợp hoặc chuyển đổi | C13, C14 | U theo A02 | Cần baseline cùng mức dịch vụ; chi phí tài nguyên, tích hợp, hỗ trợ và migration. Hiện UNKNOWN |
| R08 | Chức năng branch, federation nhiều nguồn hoặc portability mới có cần thiết không? | C01, C10, C11, C15 | I, có thể đổi thành U/B nếu xác nhận | Chưa có yêu cầu đủ cụ thể để ưu tiên một chức năng riêng hoặc thưởng điểm mặc định |

**Ví dụ truy vết:** R02 → C05/C09 → kiểm thử tài khoản chỉ được đọc một phần dữ liệu → trace, policy và dữ liệu thực thấy → PASS/FAIL/UNKNOWN → có cho phép cấu hình mới vào shortlist hay không. “Có RBAC” chưa đủ để gán PASS cho R02.

## 4. Kiểm tra ranh giới trách nhiệm trước khi so sánh

Tài liệu AWS mô tả tích hợp S3 Tables vào Glue qua federated catalog `s3tablescatalog`, ánh xạ table bucket, namespace và table sang đối tượng Data Catalog. Lake Formation tham gia kiểm soát quyền. Vì vậy, ca này cần xem **tổ hợp dịch vụ**, không thay tên Glue bằng Polaris rồi giữ nguyên mọi giả định. [S2: tích hợp S3 Tables–Glue–Lake Formation](https://docs.aws.amazon.com/lake-formation/latest/dg/create-s3-tables-catalog.html).

Các quy tắc phân công của bài đánh giá:

| Nội dung | Nơi ghi trong hồ sơ | Sai lệch cần tránh |
|---|---|---|
| Trạng thái và đường quản lý bảng | Sơ đồ S3 Tables, các endpoint và tầng federation/discovery; kiểm tra owner từng trạng thái | Gán mọi trách nhiệm metadata cho Glue |
| Phân quyền | Ma trận IAM/Lake Formation, engine và principal thực tế | Đồng nhất quyền API với quyền storage hoặc filter được thực thi trong engine |
| Maintenance bảng | Phạm vi dịch vụ S3 Tables và các tác vụ bổ sung của phương án | Ghi lợi ích compaction như một ưu thế độc lập của Glue rồi đếm lại ở chi phí |
| Chi phí | Tổng dịch vụ phụ thuộc và công thực hiện | Chỉ tính container catalog cho phương án tự vận hành |
| Hiệu năng | Đường request được đo và thành phần phụ thuộc | Quy thời gian Spark hoặc Redshift hoàn thành query cho catalog |

Tài liệu AWS cũng phân biệt đường tích hợp qua Data Catalog và đường trực tiếp qua endpoint S3 Tables; hướng dẫn được đọc là cho AWS Glue jobs, **không xác nhận phiên bản Spark Connect trên EC2 của Razor Group**. Đây là bằng chứng giúp tìm đường tích hợp, không phải phép thử R01 đã hoàn thành. [S3: các đường truy cập S3 Tables](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-integrating-glue.html).

## 5. Sàng lọc sáu công nghệ

Không có bộ release/client/policy đã được khóa hoặc kiểm thử. Bảng này chỉ sàng lọc tài liệu và định vị câu hỏi còn thiếu; **không có cấu hình nào được xác nhận PASS toàn bộ B để triển khai**.

| Công nghệ | Bằng chứng tài liệu đã đọc | Còn thiếu cho ca A01 | Xử lý sau sàng lọc |
|---|---|---|---|
| AWS Glue Data Catalog | S2 xác định đường tích hợp với backend hiện có | Phiên bản và policy thực, acceptance cho R01–R05, log/runtime và chi phí | Giữ tổ hợp hiện có làm baseline; có căn cứ tài liệu để đi vào kiểm thử, chưa có bằng chứng tối ưu |
| Apache Polaris | Tài liệu 1.8.0 mô tả federation tới external REST catalog, có AWS Glue và AWS SigV4 [S4] | Tính tương thích của endpoint S3 Tables qua Glue, identity propagation, quyền từng người dùng, read/write và Redshift; toàn bộ chưa thử | Khảo sát **Polaris bổ sung trước Glue** như một cấu hình có điều kiện. Đây chưa phải thay Glue hoặc S3 Tables |
| Apache Gravitino | Tài liệu main mô tả REST backend chuyển tiếp tới catalog khác và vị trí authorization [S5] | Release áp dụng; SigV4, policy và engine cho đúng luồng này; công thêm tầng | Có thể khảo sát cấu hình thêm tầng khi xuất hiện nhu cầu federation. Chưa chọn làm ứng viên lab |
| Project Nessie | Guide mô tả Iceberg REST và quản lý metadata; trang đang ghi đường REST experimental [S6] | Đường tới backend đang giữ, phối hợp quyền/engine, lợi ích branch trong bài toán | Giữ UNKNOWN cho R01–R04; chưa đưa vào mẫu đo. Không kết luận toàn sản phẩm thiếu trưởng thành |
| Hive Metastore | Tài liệu latest mô tả Iceberg REST/Thrift và cấu hình quyền [S7] | Đường tới backend S3 Tables và Lake Formation, release, client và policy tương ứng | Giữ UNKNOWN cho ca A01; không loại chỉ vì HMS có nguồn gốc cũ |
| Unity Catalog OSS | Trang UniForm mô tả đọc Delta UniForm qua Iceberg REST [S8] | Bằng chứng cho workflow native Iceberg trên S3 Tables và quyền/engine cần bảo toàn | Trang này chưa đủ để gán PASS hoặc FAIL. Giữ UNKNOWN; không dùng tính năng Databricks thương mại thay cho OSS |

[S4: Polaris 1.8.0 REST federation](https://polaris.apache.org/releases/1.8.0/federation/iceberg-rest-federation/) hỗ trợ một hướng tích hợp, chưa xác nhận mọi thao tác của ca. [S5: Gravitino REST backend, main](https://github.com/apache/gravitino/blob/main/docs/iceberg-rest-service.md?plain=1) cần ghim release trước thực nghiệm. [S6: Nessie Iceberg REST guide](https://projectnessie.org/guides/iceberg-rest/), [S7: HMS REST](https://hive.apache.org/docs/latest/admin/iceberg-rest-catalog/) và [S8: UC OSS UniForm](https://docs.unitycatalog.io/usage/tables/uniform/) chỉ hỗ trợ các claim hẹp nêu tại bảng.

### Hai cấu hình nghiên cứu trước mắt

- **Baseline:** Spark/engine phục vụ → đường tích hợp Glue → S3 Tables, với IAM/Lake Formation. Những mũi tên mô tả quan hệ logic; chưa phải sơ đồ mọi request/data path thực tế.
- **Cấu hình cần xác minh:** Spark → Polaris 1.8.0 federation → Glue → S3 Tables; engine phục vụ giữ đường hiện có. Cấu hình này có thêm identity, dịch vụ và failure boundary. Nó không được xem là đã khả thi chỉ vì các bên có REST.

Trước khi benchmark cặp này, phải trả lời “tầng Polaris giải quyết nhu cầu nào?”. Nếu không có mục tiêu portability/federation/identity cụ thể, chưa có lý do dùng ngân sách để đo một tầng mới. Polaris xuất hiện ở đây vì có bằng chứng cho đường tích hợp liên quan và phù hợp câu hỏi kiến trúc của đề tài; không vì tên đề tài chứng minh nó phải thắng.

Không chọn ứng viên thứ ba trước khi có một bất định quyết định mà nó có thể giải quyết. Gravitino chỉ trở thành ứng viên thứ ba nếu nhu cầu thêm tầng federation được xác định và cấu hình vượt các bước feasibility.

## 6. Khuyến nghị thu được từ lần áp dụng trên tài liệu

**Kết luận về khả năng triển khai:** chưa hình thành shortlist đã xác nhận, do các B quan trọng còn UNKNOWN ở cấu hình tái dựng. Báo cáo vận hành của nguồn không thay thế việc kiểm chứng cấu hình do sinh viên sẽ dựng.

**Khuyến nghị nghiên cứu có điều kiện:** dùng tổ hợp Glue–S3 Tables–Lake Formation làm baseline. Chưa đề xuất thay đổi production dựa trên bằng chứng đã thu thập. Tiếp tục với Polaris federation chỉ khi xác nhận mục tiêu của tầng mới và giải quyết R01–R04. Nếu bỏ A01 để đánh giá catalog trên S3 bucket thông thường, mở ca khác; phải tính phần maintenance, bảo mật và migration bị thay đổi.

Đánh đổi cần làm rõ là: lợi ích tích hợp/federation nếu có so với dịch vụ thêm, phân phối danh tính, lỗi và công vận hành. Hiện chưa có số đo để kết luận bên nào nhanh hơn, rẻ hơn hoặc tiết kiệm hơn.

**Mức chắc chắn:** có căn cứ tài liệu cho baseline và hướng khảo sát; chưa kết luận lựa chọn triển khai. Việc giữ baseline phù hợp với A02, không phải chứng minh Glue tốt nhất. Nếu người quyết định ưu tiên portability hoặc một chức năng mới, khuyến nghị nghiên cứu có thể thay đổi.

## 7. Những kiểm tra tiếp theo có thể làm — chưa thực hiện

Đây là kế hoạch bổ sung bằng chứng, không phải kết quả. Khi có môi trường AWS được phép dùng, chỉ dựng tài nguyên thử riêng và dữ liệu tổng hợp; không cần tài khoản hoặc dữ liệu của Razor Group để nghiên cứu cơ chế. Lab đó vẫn chỉ là mô hình theo kiến trúc công khai, không là tái lập production.

| Kịch bản | Mục đích và workload | Cấu hình, kiểm soát | Chỉ số và oracle | Đưa vào quyết định |
|---|---|---|---|---|
| F01 — Đường tích hợp | Writer Spark tạo/append marker; reader ở engine cần dùng đọc cùng bảng; schema change nếu yêu cầu | Khóa phiên bản, region, endpoint, API, table identity và storage; mỗi phương án dùng fixture độc lập | Marker/schema/snapshot đúng; log request và lỗi; không có hai owner độc lập công bố state của cùng bảng | R01/R03 chưa đạt thì dừng so hiệu năng trực tiếp hoặc giữ UNKNOWN để điều tra |
| F02 — Quyền và danh tính | Hai người dùng có quyền khác nhau; allow/deny/list/column filter nếu ca yêu cầu; revoke và truy cập storage | Khóa principal mapping, policy, token/cache; kiểm tra cả engine trực tiếp và qua tầng thêm | Quan sát metadata/data thực được thấy; không chỉ HTTP 403; kiểm tra tầng proxy có làm hai người dùng thành cùng một principal không | R02 không được bảo toàn thì cấu hình không phù hợp ca, dù latency tốt |
| P01 — Đọc metadata | Load/list với fixture không có writer; tải được lựa chọn từ pilot | Driver chung, cùng vị trí/region/network, tài nguyên driver đủ, cache policy rõ; cùng backend/tập policy | API latency, dispatch delay, goodput, retry, error/unknown và request counts; phản hồi đúng fixture | Đánh giá overhead của **đường có thêm tầng**, không gọi là so tốc độ thuần Polaris với Glue |
| F03/P02 — Commit và visibility | Append không tranh chấp; reader độc lập bắt đầu sau ack; thêm concurrency khi requirement cần | Cùng số bảng, thao tác, data bytes, client/retry và state ban đầu; tránh tác vụ maintenance làm đổi oracle | History, dữ liệu đã ack, duplicate/extra/unknown; attempt và logical latency; visibility contract cần xác nhận | R04 là gate theo contract; conflict hợp lệ khác lỗi dữ liệu. Không suy linearizability toàn hệ thống |
| O01 — Công vận hành và lỗi tầng thêm | Diễn tập deploy/config/rotation/upgrade; lỗi tiến trình tầng tự host nếu nằm trong yêu cầu | Runbook và operator/thứ tự ghi rõ; tách learning time với rehearsal, tổng phụ thuộc | Giờ công, task IDs, phạm vi mất chức năng và thời gian quan sát phục hồi | R06/R07 chỉ có bằng chứng lab hoặc ước tính, chưa là chi phí production |

Trước lượt đo chính thức phải chọn chỉ số chính, warm-up/reset, số lần lặp và quy tắc xử lý timeout theo pilot. Không tự đặt p95/SLO hoặc số request từ bài viết. Tính phí lab dựa trên tài nguyên thực dùng và đơn giá có ngày/region; không nhân thành chi phí năm khi chưa có workload phù hợp.

## 8. Thông tin còn thiếu và điều kiện hoàn thành ca

Các thông tin còn thiếu gồm: bộ phiên bản; metadata workload; IAM/Lake Formation và engine policy thực; yêu cầu commit, visibility và lỗi; phạm vi migration; SLO; ngân sách; và mục tiêu đủ quan trọng để thêm hoặc thay catalog.

Lần áp dụng trên tài liệu hoàn thành khi đã có nguồn, phân biệt fact/giả định, truy vết điều kiện và giải thích trạng thái UNKNOWN. Các bước đó đã được lập trong tài liệu này. Lần áp dụng thực nghiệm chỉ hoàn thành sau khi manifest và requirement được xác nhận, các phép thử liên quan được chạy, kết luận được đối chiếu với evidence và reviewer có thể tái dựng. Chưa đạt điều kiện thứ hai.

Giới hạn chính:

1. Nguồn ca là bài khách hàng trên blog nhà cung cấp, không có dữ liệu và log độc lập để tái lập. Các nguồn kỹ thuật latest/main có thể thay đổi.
2. Ca được chọn sau khi biết kiến trúc hiện có; chưa chứng minh framework dự đoán được quyết định hoặc tốt hơn cách chọn khác.
3. A01/A02 và các B dẫn xuất chưa được doanh nghiệp xác nhận; kết luận áp dụng cho ca nghiên cứu này.
4. Không quy lợi ích của toàn bộ migration hoặc giảm thời gian pipeline cho catalog. Thay đổi engine, table service và workload placement là yếu tố gây nhiễu.
5. Có tài liệu về REST hoặc S3 không chứng minh tích hợp S3 Tables, bảo toàn quyền hoặc có khả năng thay thế trực tiếp.
6. Không có benchmark, cost ledger hoặc số liệu giả làm kết quả. Chưa có căn cứ tuyên bố một catalog tốt nhất, framework đã được validation hoặc hiệu quả kinh tế đã đạt.

## 9. Hồ sơ nguồn đã đọc

| ID | Nguồn và phần đọc | Hỗ trợ | Không xác nhận |
|---|---|---|---|
| S1 | AWS Big Data Blog, *Razor Group’s journey to a modern data lakehouse on AWS*, 28/8/2026; Business challenge, Designing for scale, Phase 1, serving và migration | Ca triển khai và bối cảnh | Release/config đủ tái lập, catalog QPS/SLO hoặc so sánh sáu catalog |
| S2 | AWS Lake Formation, *Amazon S3 Tables integration with AWS Glue Data Catalog and AWS Lake Formation*; object mapping và access control | Ranh giới federation và quyền | Mọi principal/engine của doanh nghiệp đã được kiểm thử |
| S3 | Amazon S3, *Running ETL jobs on Amazon S3 tables with AWS Glue*; access methods và Spark examples | Các đường truy cập được tài liệu hóa cho Glue jobs | Cấu hình Spark Connect EC2 của ca hoặc bảo đảm tương thích với tầng proxy |
| S4 | Apache Polaris 1.8.0, *Iceberg REST Federation*; runtime requirements, authentication và operational notes | Hướng federation tới Glue, SigV4 và giới hạn remote operations | Luồng Razor, S3 Tables cụ thể, identity forwarding đúng và hiệu năng |
| S5 | Apache Gravitino, `docs/iceberg-rest-service.md` tại main; REST Backend Configuration | Có kiến trúc chuyển tiếp và vị trí authorization cần xét | Release đã ghim hoặc tương thích ca này |
| S6 | Project Nessie, *Configure Nessie with Iceberg REST*; cảnh báo và warehouse/object store | Guide và phạm vi maturity của đường REST | Không hỗ trợ S3 Tables hoặc Nessie tổng thể chưa trưởng thành |
| S7 | Apache Hive, *Iceberg REST Catalog API backed by Hive Metastore*, trang cập nhật 14/11/2025; introduction/auth | Có REST và cấu hình auth được mô tả | Đường tới S3 Tables/Lake Formation hoặc HMS không phù hợp ca |
| S8 | Unity Catalog OSS, *Unity Catalog with UniForm tables*; read Delta UniForm qua REST | Khả năng đọc trong trang được xem | Phủ định mọi native Iceberg write hoặc mọi khả năng OSS |

Việc kiểm tra nguồn ở đây là đối chiếu claim hẹp với văn bản, không kiểm tra mã nguồn, binary hoặc runtime. Tài liệu trên đủ để thực hành các bước đầu của phương pháp; các claim vượt phạm vi đó được giữ UNKNOWN.
