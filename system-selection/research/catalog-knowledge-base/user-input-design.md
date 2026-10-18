# Thiết kế input cho hệ thống hỗ trợ lựa chọn lakehouse catalog

Ngày nghiên cứu: **17/10/2026**. Trạng thái: **đề xuất thiết kế; chưa thử với người dùng, chưa chạy bộ luật hoặc đánh giá khuyến nghị**.

**Cập nhật phạm vi:** người dùng đã chốt bộ câu hỏi riêng tại [Input v1](input-v1.md). Tài liệu hiện tại được giữ làm nghiên cứu tham khảo; bộ 10 cụm đề xuất bên dưới không phải bộ input đã được người dùng chốt.

Người dùng đã xác nhận đối tượng điền form chính là **architect / người ra quyết định**. Tài liệu này đối chiếu bản đề xuất được gửi trong hội thoại với [flow lựa chọn](decision-flow.md), [cơ chế suy luận ưu tiên](advanced-reasoning.md) và nguồn chính thức. Không thay thế các tài liệu đó.

## 1. Kết luận thiết kế

Giữ hướng form có cấu trúc, hỗ trợ “chưa biết” và hỏi theo nhánh. Cần sửa cách phân loại và suy ra yêu cầu trước khi chốt giao diện. Bản gửi có **15 câu**, dù phần mở đầu ghi khoảng 14; số câu tối ưu chưa được kiểm chứng.

Đầu vào cần diễn đạt riêng bốn thứ:

1. **Bối cảnh hiện tại:** đang dùng gì, hệ thống nào đã tồn tại.
2. **Yêu cầu đích và ràng buộc:** cần thực hiện việc gì, điều gì bắt buộc giữ và điều gì được thay đổi.
3. **Ưu tiên:** chấp nhận đánh đổi gì giữa các lựa chọn đều khả thi.
4. **Phạm vi chưa biết:** thiếu thông tin người dùng hay thiếu bằng chứng về catalog.

Chỉ thông tin hiện trạng chưa đủ để chọn một công nghệ duy nhất. Ngược lại, việc người dùng thích một công nghệ không chứng minh công nghệ đó đáp ứng yêu cầu. Thu thập và xử lý hai loại thông tin này riêng.

Phạm vi kế thừa của prototype: Hive Metastore, AWS Glue Data Catalog, Apache Polaris, Project Nessie, Apache Gravitino, **Unity Catalog OSS**. Databricks, Snowflake và các dịch vụ thương mại có thể là bối cảnh tích hợp, không tự trở thành ứng viên mới. Nếu nhu cầu vượt phạm vi sáu công nghệ, cần trả kết quả ngoài phạm vi hoặc cần mở rộng nghiên cứu; không ép một lựa chọn trong danh sách thắng.

## 2. Nguyên tắc hỏi đã điều chỉnh

| Nguyên tắc trong bản gửi | Điều chỉnh đề xuất |
|---|---|
| Người dùng trả lời ngay, không cần tra cứu | Dùng làm mục tiêu giảm công sức. Với architect, cho phép lưu và bổ sung thông tin từ chính sách, SLA hoặc inventory; thông tin thiết yếu không nên bị bỏ chỉ vì cần xác nhận nội bộ |
| Mọi câu phải đổi kết quả | Câu hỏi phải đổi ít nhất một hành động: sàng lọc, giải thích, mức kiểm chứng, nhánh hỏi hoặc so sánh. Không bắt buộc đổi catalog đứng đầu trong mọi ca |
| Chỉ có lựa chọn, không điền số | Ưu tiên lựa chọn cho bối cảnh phổ biến. Cho phép tên khác, phiên bản, vùng được phép và ngưỡng đã biết. Không ép một chính sách thật vào khoảng số tùy ý |
| Chỉ hỏi sự thật | Hỏi sự thật để kiểm tra điều kiện; hỏi quyết định và đánh đổi để xác định ưu tiên. Tránh câu mơ hồ như “linh hoạt mức mấy?” |
| Mọi câu có “chưa biết” | Cho phép khi có ý nghĩa, đồng thời phân biệt với không cần, chưa chọn, chưa trả lời và ngoài phạm vi |

GOV.UK khuyến nghị lập *question protocol*: vì sao cần thông tin, ai cần trả lời, dùng câu trả lời thế nào và kiểm tra ra sao; đồng thời dùng phân nhánh để chỉ hỏi phần liên quan. Đây là căn cứ thiết kế form, không phải bằng chứng về số câu phù hợp cho architect chọn catalog. [S1](https://www.gov.uk/service-manual/design/form-structure)

GOV.UK cũng khuyến nghị câu hỏi dễ hiểu và cho phép “không biết” khi hợp lệ. Ngôn ngữ nên đi từ tác vụ người dùng sang thuật ngữ kỹ thuật; ví dụ nghiệp vụ không thay cho xác nhận yêu cầu. [S2](https://www.gov.uk/service-manual/design/designing-good-questions)

## 3. Những suy luận cần sửa trước khi xây luật

### 3.1. Hiện trạng không tự là ràng buộc bắt buộc

“Đang chạy trên AWS” không đồng nghĩa “chỉ được dùng dịch vụ catalog của AWS”. “Đang có hợp đồng Databricks” không đồng nghĩa “bắt buộc chọn Unity Catalog OSS”. Hỏi thêm phần nào phải giữ, thời hạn áp dụng và thay đổi nào được phép.

Tách **nơi chạy engine**, **nơi lưu dữ liệu**, **nơi được đặt catalog/control plane** và **khả năng kết nối**. Ví dụ engine on-prem, dữ liệu S3 và catalog quản lý trên cloud chưa tự mâu thuẫn. Tài liệu Trino liệt kê riêng yêu cầu truy cập storage và truy cập metastore/catalog; AWS mô tả endpoint REST để client kết nối Glue. Từ đó, thiết kế này yêu cầu kiểm tra từng đường kết nối thay vì loại bằng một nhãn cloud. Hai tài liệu không chứng minh mọi tổ hợp hybrid đều chạy được. [S3](https://trino.io/docs/current/connector/iceberg.html), [S4](https://docs.aws.amazon.com/glue/latest/dg/connect-glu-iceberg-rest.html)

### 3.2. Tên engine chưa đủ xác nhận tương thích

“Spark + Trino” còn thiếu: engine nào đọc, engine nào ghi, ghi kiểu gì, trên format nào, phiên bản nào và phần nào bắt buộc giữ. Trino và Presto, StarRocks và Doris phải có định danh riêng khi tra tri thức. Có thể nhóm chúng trên giao diện khám phá, nhưng không dùng một claim hỗ trợ chung cho cả nhóm.

Chọn Iceberg và Delta phải làm rõ **cần cả hai**, **chấp nhận một trong hai**, hay **chưa quyết định**. Nếu giữ nhiều nguồn, nối engine với đúng tập bảng/format; không tự tạo tích Descartes mọi engine × mọi format.

### 3.3. Nhiều writer hoặc streaming không suy ra giao dịch nhiều bảng

Số team, số engine, số job và số thao tác ghi đồng thời là các đại lượng khác nhau. Một engine có thể chạy nhiều job tranh chấp cùng bảng. Nhiều team có thể chỉ đọc hoặc ghi vào các bảng tách biệt.

Iceberg mô tả concurrent writes bằng optimistic concurrency và retry. Nessie mô tả riêng việc công bố thay đổi nhiều bảng qua branch/merge và các khả năng còn phụ thuộc tích hợp công cụ. Vì vậy không ánh xạ “streaming = có” thành “cần multi-table transaction”, hoặc “Nessie hỗ trợ primitives” thành “mọi engine dùng được SQL transaction nhiều bảng”. [S5](https://iceberg.apache.org/docs/1.9.2/reliability/), [S6](https://projectnessie.org/guides/transactions/)

### 3.4. Chính sách quyền cần có phạm vi thực thi

Phân biệt quyền trên metadata/catalog, quyền đọc dữ liệu, lọc hàng, che cột và quyền truy cập object storage. Hỏi chính sách phải có hiệu lực qua engine nào, có đường truy cập trực tiếp nào được phép và tổ chức chấp nhận thành phần thực thi bổ sung nào.

Thay câu đầu tiên “cần credential vending không?” bằng: “Engine có cần lấy quyền storage tạm thời, giới hạn theo dữ liệu được phép, thay vì được cấp quyền storage dài hạn riêng không?”. Cho phép “chính sách khác/chưa quyết định”. Khi nhu cầu đó có, mới xác nhận cơ chế chấp nhận được: vending, signing hoặc cơ chế được duyệt khác. Polaris mô tả credentials ngắn hạn và có scope cho client truy cập storage; điều đó không tự chứng minh lọc hàng/cột. [S7](https://polaris.apache.org/releases/1.7.0/vended-credentials/)

### 3.5. Năng lực vận hành không thay cho ngân sách hoặc chính sách

Không suy ngân sách từ số người trong đội; không suy self-host yêu cầu Kubernetes + PostgreSQL cho mọi công nghệ. Cần biết đơn vị nào chịu vận hành, dịch vụ nền tảng nào sẵn có, mô hình thuê ngoài được phép và yêu cầu hỗ trợ. “On-prem + đội data không tự vận hành” có thể có đội hạ tầng hoặc nhà thầu đảm nhiệm.

Không cần ép nhập ngân sách chính xác ở lần đầu. Nếu có trần đã duyệt thì cho nhập kèm tiền tệ, kỳ tính và phạm vi chi phí. Chưa có bằng chứng chi phí so sánh được thì không khẳng định một ứng viên rẻ hơn hoặc nằm trong ngân sách.

## 4. Bộ input đề xuất cho prototype

Đề xuất **10 cụm thông tin ban đầu**, sau đó hỏi theo nhánh. Một cụm có thể có nhiều trường hoặc hàng; đây không phải cam kết người dùng chỉ trả lời đúng 10 thao tác. Số màn hình, số câu hiện ra và thời gian hoàn thành phải được đo trong thử nghiệm.

| ID | Câu hỏi/cụm thông tin hiển thị | Lựa chọn hoặc cách trả lời | Vai trò trong xử lý |
|---|---|---|---|
| Q01 | **Bạn đang cần quyết định việc gì?** | Chọn cho hệ thống mới / thay catalog hiện có / giữ hệ thống và bổ sung khả năng / đánh giá lựa chọn hiện tại / chưa rõ. Ghi riêng phạm vi thử nghiệm hay production | Chọn kịch bản; không đồng nhất có catalog sẵn với bắt buộc di chuyển |
| Q02 | **Dữ liệu thuộc phạm vi lựa chọn đang hoặc sẽ nằm ở đâu?** | AWS S3 / ADLS-Blob / GCS / HDFS / storage tương thích S3, có tên sản phẩm nếu biết / khác / chưa chọn / chưa biết; chọn nhiều khi cần | Tạo inventory storage. Đánh dấu riêng nguồn nào bắt buộc giữ; nhãn “S3-compatible” chưa đủ chứng minh mọi chức năng |
| Q03 | **Những môi trường nào phải truy cập cùng tập dữ liệu?** | AWS / Azure / GCP / trung tâm dữ liệu riêng / môi trường khác; chọn nhiều và gắn engine ở Q05 vào môi trường nếu cần | Xác định topology thực tế; mở câu hỏi vị trí control plane và kết nối khi liên quan |
| Q04 | **Định dạng bảng nào cần tiếp tục sử dụng?** | Iceberg / Delta / Hudi / Hive tables không dùng ba format đó / khác / chưa chọn / chưa biết. Với nhiều lựa chọn: cần tất cả hay đang chọn giữa các phương án | Xác định format cần hỗ trợ và tính linh hoạt; không coi chưa chọn là hỗ trợ mọi format |
| Q05 | **Engine nào cần làm thao tác gì trên dữ liệu đó?** | Mỗi hàng: engine → tập dữ liệu/format → chỉ đọc / thêm dữ liệu / sửa-xóa-merge / quản lý cấu trúc bảng / chưa rõ. Phần đã có và dự kiến ghi riêng | Tạo ma trận engine–thao tác–format; các hàng bắt buộc được xét đồng thời |
| Q06 | **Workflow nào hệ thống cần hỗ trợ?** | Chia sẻ cùng bảng cho nhiều engine / ghi đồng thời cùng bảng / chuẩn bị thay đổi ở nhánh riêng rồi công bố / công bố đồng bộ thay đổi nhiều bảng / quản lý chung nhiều catalog hoặc nguồn / chưa có workflow bổ sung / chưa rõ | Kích hoạt yêu cầu có ngữ nghĩa. Chọn một workflow mở câu xác nhận phạm vi; không cộng điểm theo số ô chọn |
| Q07 | **Các nhóm/người dùng cần bị giới hạn truy cập như thế nào?** | Chỉ cần quản lý metadata / phân quyền bảng / lọc hàng / che hoặc giới hạn cột / cô lập tenant / chưa có yêu cầu xác nhận. Các nhu cầu có thể chọn đồng thời | Hỏi tiếp điểm thực thi, engine phải tuân thủ và mô hình quyền storage; “quản trị tốt” không là một tiêu chí đủ rõ |
| Q08 | **Ai có thể chịu trách nhiệm vận hành dịch vụ catalog?** | Đội data / đội platform-hạ tầng / nhà cung cấp hoặc nhà thầu / chấp nhận nhiều mô hình / chưa có đơn vị nhận. Ghi riêng mô hình được tổ chức cho phép | Đánh giá khả thi vận hành; chưa có owner mở việc cần xác nhận, không tự cấm mọi hình thức self-host |
| Q09 | **Có chính sách hoặc cam kết nào bắt buộc tuân thủ khi lựa chọn không?** | Vị trí dữ liệu-metadata / kết nối mạng / định danh / giấy phép OSS / điều khoản thương mại / ngân sách / hỗ trợ-SLA / không có điều kiện bổ sung đã xác nhận / chưa rà soát | Đây là câu kích hoạt; phải thu chi tiết điều kiện được chọn trước khi dùng để loại ứng viên |
| Q10 | **Sau khi đáp ứng điều kiện bắt buộc, bạn muốn cải thiện điều gì trước?** | Chọn tối đa hai để bắt đầu: giảm công vận hành / giảm tổng chi phí / giảm công-rủi ro di chuyển / mở rộng engine-nguồn dữ liệu / thực thi quản trị nhất quán / workflow kiểm thử-công bố thay đổi / khác / chưa quyết định | Chọn đánh đổi cần làm rõ; lựa chọn và thứ tự chưa tự tạo trọng số hoặc quy tắc ưu tiên tuyệt đối |

Mỗi mục chọn nhiều phải có lựa chọn loại trừ phù hợp như “không có/chưa biết”; không cho chọn chúng cùng các mục xác nhận cụ thể. Riêng dữ liệu biết một phần nên ghi trạng thái từng hàng, không ép người dùng chọn biết hết hoặc không biết gì.

Sau khi nhập, hiển thị bản tóm tắt để xác nhận: **đang có**, **phải giữ/đáp ứng**, **được thay đổi**, **ưu tiên**, **chưa xác nhận**. Chỉ tạo B từ xác nhận yêu cầu, không mặc định mọi giá trị hiện trạng là B. Một yêu cầu có thể vừa có minimum B vừa có mục tiêu U cao hơn, lưu hai phần riêng.

## 5. Câu hỏi theo điều kiện

| Nhánh | Khi nào cần hỏi | Thông tin cần thu và tác động |
|---|---|---|
| F01 Catalog hiện có và migration | Q01 là thay thế, mở rộng hoặc đánh giá hệ thống đang có | Tên catalog, phạm vi sử dụng; có bắt buộc giữ dữ liệu tại chỗ, lịch sử snapshot, identifier, grants, ứng dụng, rollback và thời gian gián đoạn không? Hỏi từng điều kiện liên quan; không suy tất cả phải giữ |
| F02 Phiên bản và thay đổi cho phép | Tính tương thích phụ thuộc engine/client/format/release | Phiên bản nếu biết; có được nâng cấp/thêm connector không? Không biết thì giữ kết luận có điều kiện và chỉ rõ cần xác minh |
| F03 Phạm vi workflow | Q06 có branch, nhiều bảng hoặc federation | Phân biệt nhánh một bảng với cả tập bảng; yêu cầu công bố visibility với transaction SQL; danh sách nguồn/catalog phải quản lý. Không suy branch cấp bảng tương đương branch cấp catalog |
| F04 Tranh chấp ghi | Q06 có ghi đồng thời hoặc người dùng khai báo lỗi xung đột | Nhiều job có ghi cùng bảng, cùng thời điểm không? Append, merge, overwrite hay maintenance? Nếu cần, thu số writer đồng thời và độ trễ/khả năng retry chấp nhận được |
| F05 Streaming và tải metadata | Quy mô/commit/SLO có thể phân biệt ứng viên | Batch/stream/microbatch, nhịp commit nếu biết, hot tables, số bảng và request mix. Không suy commit rate từ TB dữ liệu hoặc từ nhãn streaming |
| F06 Chính sách truy cập | Q07 có yêu cầu quyền hoặc Q09 có chính sách định danh | Engine/đường truy cập phải tuân thủ; IdP cần dùng; cấp quyền storage tạm thời hay mô hình được duyệt khác; ai thực thi row/column policy? Audit sự kiện và lineage hỏi riêng |
| F07 Residency và mạng | Q09 chọn vị trí hoặc kết nối | Quốc gia/vùng được phép, áp dụng cho dữ liệu hay cả metadata/log/backup; catalog có được gọi dịch vụ ngoài và có được kết nối tới engine/storage không? Thu chính sách tổ chức, không suy nghĩa vụ pháp lý từ tên ngành |
| F08 Cam kết thương mại | Q09 có hợp đồng, license, ngân sách hoặc support | Điều khoản nào thực sự ràng buộc, chỉ là tài sản hiện có hay ưu tiên? Trần chi phí gồm dịch vụ, hạ tầng, nhân công và migration nào, tính trong kỳ nào? Unity Catalog OSS được đánh giá theo bằng chứng OSS |
| F09 Mức dịch vụ và phục hồi | Production có mục tiêu đã cam kết hoặc so sánh phụ thuộc độ sẵn sàng | SLO, RTO/RPO, support và mức chấp nhận feature thử nghiệm; cho phép nhập giá trị/ngưỡng được duyệt, hoặc đánh dấu cần xác nhận. Prototype không mặc nhiên là xác nhận đáp ứng production |
| F10 Đánh đổi giữa hồ sơ | Có từ hai ứng viên khả thi còn khác nhau trên ưu tiên liên quan | Trình bày chênh lệch có bằng chứng và hỏi ưu tiên hồ sơ A/B / tương đương / chưa đủ thông tin. Tình huống giả định phải gắn nhãn; không dùng số tiền/giờ công bịa như dữ liệu sản phẩm |

Nhu cầu quản lý nhiều nguồn đáng có câu hỏi riêng vì Gravitino định nghĩa lớp quản lý metadata nhiều loại nguồn và connector. Đây là căn cứ đưa workflow vào bộ hỏi; không tự chứng minh Gravitino thắng khi chọn ô federation. [S8](https://gravitino.apache.org/docs/1.0.0/overview/)

## 6. Rà lại từng câu trong bản đề xuất ban đầu

| Câu cũ | Xử lý đề xuất | Lý do |
|---|---|---|
| A1 Nơi chạy | Tách Q02/Q03 và F07 | Storage, compute và vị trí catalog là các biến khác nhau |
| A2 Engine | Giữ, mở thành Q05 và F02 | Cần thao tác, format, phiên bản khi ảnh hưởng kết luận |
| A3 Table format | Giữ, sửa thành Q04 | Tách hiện tại/đích, bắt buộc giữ và AND/OR |
| A4 Catalog hiện có | Đưa F01 sau Q01 | Có catalog chưa quyết định đang muốn thay hay chỉ bổ sung |
| A5 Hợp đồng nền tảng | Đưa F08 | Chỉ điều khoản cụ thể mới tạo ràng buộc; tránh thiên kiến thương hiệu |
| B1 Số bảng | Đưa F05 | Chỉ dùng khi có claim/benchmark cùng phạm vi; không tự đặt ngưỡng “trên 10.000 thì loại X” |
| B2 Số engine/team cùng ghi | Thay bằng workflow Q06 và F04 | Team/engine không đo trực tiếp concurrency hoặc contention |
| B3 Streaming | Giữ trong F05 | Cần mô hình commit và thao tác; không suy ra transaction semantics |
| C1 Mức phân quyền | Giữ, cụ thể hóa Q07/F06 | Thang bảng → cột-hàng không mô tả đầy đủ các đường thực thi |
| C2 Credential vending | Hỏi nhu cầu quyền storage trước, cơ chế sau | Tránh bắt người dùng chọn giải pháp trước khi xác định yêu cầu |
| C3 Dữ liệu trong khu vực | Giữ Q09/F07 | Cần biết vùng nào, phạm vi dữ liệu nào, và catalog có được đặt ngoài không |
| C4 Audit/lineage | Tách hai nhu cầu trong F06 | Hai tính năng không tương đương; cũng cần hỏi chấp nhận tích hợp ngoài hay phải có sẵn |
| D1 Số người trong đội | Bỏ khỏi lõi; chỉ hỏi effort/capacity khi cần | Headcount không đủ suy chi phí, khả năng trực vận hành hoặc kỹ năng |
| D2 Tự host Kubernetes + Postgres | Thay Q08 | Không áp một kiến trúc phụ thuộc cho mọi catalog; “ngại” không phải năng lực thực tế |
| D3 Dùng thêm vendor trong hai năm | Hỏi trong Q05/Q10 khi có kế hoạch | Phân biệt đã phê duyệt, dự kiến và chỉ muốn giữ lựa chọn. Không tự biến dự đoán thành điều kiện bắt buộc |

## 7. Ngữ nghĩa dữ liệu và luật xử lý

### 7.1. Trạng thái câu trả lời và trạng thái đánh giá

| Trạng thái input | Ví dụ | Cách xử lý |
|---|---|---|
| Biết giá trị | Đang lưu ở S3 | Lưu sự thật; hỏi phần nào phải giữ nếu chưa rõ |
| Không có đối tượng | Chưa có catalog | Giá trị xác nhận của inventory, không phải dữ liệu bị thiếu |
| Không có yêu cầu | Không bắt buộc giữ catalog hiện tại | Không tạo ràng buộc bảo toàn catalog đó |
| Chưa quyết định | Chưa chọn table format | Giữ các lựa chọn cho phép; có thể cần một quyết định liên quan trước khi khuyến nghị chắc chắn |
| Chưa biết | Không biết công ty có cấm metadata ra ngoài không | Không mặc định không có hạn chế; yêu cầu liên quan còn mở |
| Chưa trả lời | Bỏ qua trường | Ghi riêng, không tự đồng nhất với “không” |
| Không áp dụng | Câu migration khi xây hoàn toàn mới | Bỏ nhánh có lý do; không dùng trạng thái này để né yêu cầu bắt buộc |

Trạng thái input khác với `PASS/FAIL/UNKNOWN/N/A` khi đánh giá catalog. Không quy “không biết nhu cầu” thành “catalog không hỗ trợ”. Không quy “KB thiếu bằng chứng” thành yêu cầu người dùng tự biết khả năng sản phẩm.

### 7.2. Bản ghi tối thiểu cho một yêu cầu

Lưu: ID câu trả lời gốc; hiện tại/đích/kế hoạch; phát biểu chuẩn hóa; B/U/I hoặc chưa xác nhận; điều kiện áp dụng; thao tác và tài nguyên; AND/OR; ngưỡng và đơn vị nếu có; nguồn xác nhận; phần cho phép thay đổi; revision; lý do luật ánh xạ.

Ví dụ người dùng xác nhận “phải giữ S3, Trino chỉ cần đọc, Spark phải đọc và append trên cùng bộ bảng Iceberg” tạo các yêu cầu sau:

| Yêu cầu | Mức | Kiểm tra |
|---|---|---|
| Tiếp tục dùng dữ liệu ở S3 trong phạm vi đã xác định | B | Đường truy cập storage phù hợp và được phép |
| Trino đọc được tập bảng đó | B | Đúng engine/format/client và thao tác |
| Spark đọc và append được tập bảng đó | B | Đúng thao tác và điều kiện đồng tồn tại với Trino |
| Giảm công vận hành | U nếu người dùng chọn | Dữ liệu effort có phạm vi so sánh, sau đó hỏi đánh đổi khi cần |

Ví dụ này **không** tự tạo yêu cầu multi-table transaction, không bắt buộc catalog do AWS vận hành và không yêu cầu Trino ghi. Nếu chưa biết phiên bản liên quan, cần ghi giới hạn chứng minh tương thích; chưa được gọi là cấu hình đã xác nhận triển khai.

### 7.3. Ưu tiên không phải trọng số ẩn

Q10 chỉ định hướng hỏi. Không đổi “chi phí, vận hành” thành 60/40, cũng không coi thứ tự đó là ưu tiên tuyệt đối. Phản hồi so sánh hồ sơ có thể bổ sung quan hệ ưu tiên vào mô hình hiện có; nếu dữ liệu/thang giá trị chưa đủ, giữ shortlist và giải thích đánh đổi.

Nghiên cứu về preference elicitation xem việc chọn câu hỏi như một phần của cải thiện quyết định, nhưng có mô hình và yêu cầu dữ liệu riêng. Bài IJCAI 2024 dùng mô hình học từ dữ liệu để ước tính EVOI. Prototype chưa có các thành phần đó thì chỉ nên gọi cơ chế thử các đáp án là **heuristic hỏi theo tác động quyết định**. [S9](https://www.ijcai.org/proceedings/2024/387)

### 7.4. Mâu thuẫn và thiếu lời giải

- On-prem + AWS-native: cần làm rõ topology/commitment, chưa phải mâu thuẫn.
- Không có đội data vận hành + on-prem: hỏi owner hạ tầng/thuê ngoài, chưa phải mâu thuẫn.
- “Cấm metadata ra ngoài mạng nội bộ” + “catalog bắt buộc nằm ngoài mạng đó và phải nhận metadata”: có thể xung đột trực tiếp nếu cùng phạm vi, thời điểm và không có ngoại lệ; yêu cầu người dùng sửa hoặc làm rõ.
- Không có ứng viên trong KB đáp ứng: có thể do phạm vi ứng viên hoặc thiếu bằng chứng; không tự kết luận câu trả lời mâu thuẫn.
- Một đường tích hợp không đáp ứng: chưa đủ loại toàn công nghệ nếu còn đường được phép nhưng chưa xác minh. Kiểm tra phạm vi nhất quán theo flow hiện hành.

## 8. Hỏi bổ sung và hiển thị kết quả

Sau mỗi lần chuẩn hóa, xét câu còn thiếu có thể làm đổi tập đủ điều kiện, trạng thái chưa xác minh hoặc quan hệ ưu tiên không. Ưu tiên làm rõ điều kiện bắt buộc trước khi hỏi đánh đổi. Không hỏi sâu các trường không còn giúp quyết định, trừ thông tin người dùng cần để hiểu giới hạn kết luận.

Một câu bị trả lời “chưa biết” nhiều có thể khó hiểu, hỏi sai người, chưa được tổ chức quyết định hoặc thực sự cần tra cứu. Phải tìm nguyên nhân trước khi xóa hoặc đổi thành câu gián tiếp. Không dùng tỷ lệ chưa biết đơn độc làm tiêu chí bỏ câu.

Output cần hiển thị:

- Công nghệ hoặc shortlist, trong tập sáu công nghệ và snapshot bằng chứng đang dùng.
- Các yêu cầu bắt buộc đã xác nhận; lý do phù hợp, loại hoặc cần xác minh.
- Giả định và thông tin còn mở có thể đổi kết quả; chỉ gọi “có thể đổi” khi đã phân tích nhánh hoặc có lập luận rõ.
- Việc tiếp theo thuộc người dùng hay người biên soạn KB; không trộn hai trách nhiệm.
- Revision câu trả lời, luật và bằng chứng để tái lập kết quả.

Không hiển thị “độ phù hợp 92%” từ số câu đã điền, tỷ lệ kịch bản thắng hoặc số tính năng khớp. Khi thông tin quá thiếu, trả trạng thái cần bổ sung hoặc danh sách khám phá có nhãn rõ.

## 9. Bộ ca phát triển đề xuất

Các ca dưới đây **hoàn toàn giả định**, mới kiểm tra bằng lập luận yêu cầu. Chưa chạy inference engine, không phải kết quả đánh giá sản phẩm hoặc oracle chuyên gia. Mục tiêu là xác định hành vi form và luật cần kiểm tra.

| Ca | Input trọng tâm | Hành vi mong đợi |
|---|---|---|
| T01 AWS, Iceberg, Spark ghi, Trino đọc | Mọi tích hợp đó phải giữ | Sinh đúng ma trận thao tác; không chỉ còn Glue vì nhãn AWS |
| T02 Engine on-prem, dữ liệu S3 | Cho phép kết nối tới catalog cloud | Không báo mâu thuẫn; kiểm tra storage, kết nối, auth và chính sách riêng |
| T03 On-prem, đội data không nhận vận hành | Có đội platform đảm nhiệm | Giữ khả năng self-host nếu mô hình và yêu cầu còn lại cho phép |
| T04 Iceberg + Delta, cần cả hai | Engine A chỉ dùng Iceberg, B chỉ dùng Delta | Dùng AND giữa các nhu cầu thực, không đòi A và B đều thao tác mọi format |
| T05 Một engine, nhiều job streaming append cùng bảng | Không cần công bố đồng bộ nhiều bảng | Mở concurrency/tải; không tự tạo B về multi-table transaction |
| T06 Chuẩn bị một tập bảng ở nhánh riêng rồi công bố | Không có streaming | Mở phạm vi branch/visibility; kiểm chứng tích hợp, không cần B3 mới hỏi |
| T07 Giữ Hive/Glue và cần quản lý thêm nguồn quan hệ | Chưa yêu cầu di chuyển bảng | Mở federation/phạm vi nguồn; không ép thành lựa chọn thay thế toàn bộ |
| T08 Row filtering qua Spark và Trino, cho phép storage access cụ thể | Chính sách phải có hiệu lực trên cả hai đường | Hỏi enforcement và bypass; không coi credential vending là bằng chứng đủ |
| T09 Đang trả phí Databricks, chưa có điều khoản khóa lựa chọn | Chỉ sáu ứng viên hiện hành | Lưu bối cảnh; không tự gán khả năng managed cho Unity Catalog OSS |
| T10 Chưa biết chính sách metadata và chưa chọn format | Không đủ điều kiện đích để chứng minh fit | Chỉ rõ thông tin còn thiếu, không gán mặc định không hạn chế hoặc chọn một catalog chắc chắn |

Các phép kiểm tra bổ sung: đổi thứ tự câu hỏi không đổi kết quả với cùng yêu cầu chuẩn hóa; thêm ràng buộc B trên cùng snapshot không mở rộng tập đủ điều kiện; lặp một lợi ích không tăng ưu tiên; đổi current sang must-keep phải có truy vết; rút một quyết định đã xác nhận phải vô hiệu hóa câu trả lời con không còn áp dụng mà vẫn giữ lịch sử.

## 10. Cách đánh giá trước khi chốt form

1. Dùng các ca phát triển để viết bảng **câu hỏi → giá trị → yêu cầu → luật/claim → hành động khi thiếu**. Câu chưa có cách sử dụng rõ để ngoài lõi.
2. Kiểm tra từng câu trong các ngữ cảnh áp dụng; xét cả tương tác với câu khác. Câu chỉ thay đổi giải thích hoặc nghĩa vụ xác minh có thể vẫn cần giữ.
3. Cho architect/platform lead đọc từng câu và diễn giải lại ý nghĩa; quan sát chỗ họ phải đoán, cần tra cứu hoặc hiểu sai hiện tại/bắt buộc.
4. So form cố định với form theo nhánh trên ca riêng, với cùng KB và chuẩn tham chiếu. Đo số trường thực sự hiển thị, thời gian, sửa câu trả lời, thiếu/misclassify B, câu hỏi thừa và mức khuyến nghị đúng phạm vi.
5. Báo riêng số ca có thể kết luận, shortlist và thiếu bằng chứng. Không coi hệ luôn từ chối là chất lượng cao chỉ vì ít chọn sai. Kết quả lựa chọn có thể là một tập hợp hợp lệ, không nhất thiết một nhãn duy nhất.

Các con số về số câu, số người thử hoặc thời gian kỳ vọng trong thiết kế chỉ là quyết định pilot khi được đặt rõ. Chưa có căn cứ nghiên cứu này chứng minh 10 cụm hoặc một thời gian hoàn thành cụ thể là tối ưu.

## 11. Phạm vi nguồn đã đọc

Nguồn được truy cập ngày **17/10/2026**. Đây là nghiên cứu tập trung về input, không phải systematic review hoặc cập nhật toàn bộ ma trận tính năng sáu công nghệ. Nguồn động và tài liệu có phiên bản được dùng đúng phạm vi dưới đây.

| Nguồn | Phần dùng | Giới hạn |
|---|---|---|
| S1 GOV.UK, Structuring forms | Question protocol, branching, cấu trúc form | Hướng dẫn dịch vụ công; áp dụng cho miền catalog là suy luận thiết kế |
| S2 GOV.UK, Designing good questions | Dễ hiểu, câu đóng, “chưa biết”, thử câu hỏi | Không chứng minh architect sẽ trả lời chính xác mọi câu |
| S3 Trino, Iceberg connector; trang lúc đọc ghi Trino 484 | Requirements, cấu hình catalog/filesystem, giới hạn format theo trang | Không dùng để xác nhận mọi release hoặc toàn bộ ma trận thao tác |
| S4 AWS Glue, Iceberg REST endpoint | Cách client kết nối catalog endpoint và phạm vi storage được trang mô tả | Không kết luận mọi topology on-prem/cloud hoặc storage đều được hỗ trợ |
| S5 Apache Iceberg 1.9.2, Reliability | Concurrent writes, optimistic concurrency/retry | Là căn cứ phân biệt khái niệm, không là benchmark catalog |
| S6 Project Nessie, Transactions | Cross-table qua branch/single commit và giới hạn tích hợp công cụ | Không khẳng định mọi engine đã hỗ trợ transaction nhiều bảng |
| S7 Apache Polaris 1.7.0, Vended Credentials Reference | Credentials tạm thời có scope, client truy cập storage trực tiếp | Không chứng minh row/column enforcement hoặc tương thích mọi storage |
| S8 Apache Gravitino 1.0.0, Overview | Mô hình nguồn/connector và unified metadata management | Không dùng overview để chứng minh từng connector hoặc tính năng production |
| S9 Martin và cộng sự, IJCAI 2024 | Abstract về preference elicitation, EVOI và mô hình học từ dữ liệu | Chỉ đọc abstract cho lượt này; không kế thừa bảo đảm hoặc kết quả thực nghiệm của bài cho catalog |

Các đề xuất về bộ hỏi, cấu trúc trạng thái, thứ tự hỏi và bộ ca là **thiết kế cho đề tài này**, cần prototype và đánh giá tiếp.
