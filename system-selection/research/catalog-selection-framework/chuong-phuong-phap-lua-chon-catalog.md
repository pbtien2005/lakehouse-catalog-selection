# Phương pháp lựa chọn công nghệ Catalog

## 1. Mục tiêu và phạm vi

Chương này đề xuất phương pháp chuyển yêu cầu của một hệ thống dữ liệu thành danh sách phương án catalog phù hợp và khuyến nghị có căn cứ. Kết quả lựa chọn cần trả lời được bốn câu hỏi: phương án nào đáp ứng các yêu cầu bắt buộc; các phương án còn lại khác nhau ở những đánh đổi nào; bằng chứng nào hỗ trợ khuyến nghị; và trong điều kiện nào khuyến nghị có thể thay đổi.

Phạm vi đánh giá là technical catalog trong hệ sinh thái Big Data, với sáu công nghệ được khảo sát gồm Hive Metastore, AWS Glue Data Catalog, Apache Polaris, Project Nessie, Apache Gravitino và Unity Catalog OSS. Enterprise catalog và business catalog chỉ được đề cập để làm rõ bối cảnh. Việc phân tích sâu Apache Polaris phục vụ mục tiêu nghiên cứu kiến trúc của đề tài, không tạo ưu tiên mặc định cho Polaris trong quá trình lựa chọn.

Đơn vị đánh giá là **một phương án triển khai cụ thể**, bao gồm sản phẩm và phiên bản, giao diện sử dụng, backend lưu trạng thái, engine và client, table format, storage, cơ chế xác thực và phân quyền, tài nguyên cùng cấu hình liên quan. Một kết luận về phương án này không tự động áp dụng cho mọi phiên bản hoặc cách triển khai của cùng sản phẩm. Các dịch vụ phụ thuộc cần thiết, chẳng hạn cơ sở dữ liệu, dịch vụ danh tính hoặc dịch vụ thực thi chính sách, được ghi nhận trong phạm vi đánh giá.

Phương pháp được tổ chức theo mạch: xác định yêu cầu → lọc điều kiện bắt buộc → thu thập bằng chứng và đánh giá theo kịch bản → phân tích đánh đổi → hình thành khuyến nghị → kiểm tra độ nhạy. Không bắt buộc tạo thứ hạng duy nhất hoặc quy mọi đặc điểm thành điểm số.

Tại thời điểm xây dựng chương, đề tài chưa có hồ sơ yêu cầu được xác nhận cho một dự án Viettel cụ thể. Các yêu cầu về tải, mức dịch vụ, hạ tầng, ngân sách và năng lực vận hành vì vậy vẫn cần được làm rõ. Kế hoạch kiểm thử và benchmark trình bày dưới đây chưa được thực hiện; chương này mô tả phương pháp nghiên cứu, chưa cung cấp kết quả lựa chọn công nghệ hay hiệu quả kinh tế.

## 2. Cơ sở phương pháp

### 2.1. Các nguyên tắc kế thừa

Nghiên cứu của Bjarnason, Åberg và Ali xây dựng mô hình lựa chọn phần mềm thông qua kết hợp tổng quan nghiên cứu với nhu cầu của tổ chức sử dụng. Đề tài kế thừa cách xuất phát từ bối cảnh, xác định tiêu chí liên quan, sàng lọc và đánh giá các phương án. Tuy nhiên, mô hình trong nghiên cứu gốc được xây dựng và kiểm chứng trong bối cảnh doanh nghiệp cụ thể; kết quả đó không xác nhận tính phù hợp của bộ tiêu chí catalog tại Viettel. [[1]](https://link.springer.com/article/10.1007/s10664-023-10288-w)

Farshidi và cộng sự phân biệt yêu cầu cứng và yêu cầu mềm trong hệ thống hỗ trợ lựa chọn công nghệ. Nghiên cứu cũng chỉ ra nhu cầu bổ sung đánh giá hiệu năng và tổng chi phí sở hữu khi xem xét phương án. Đề tài kế thừa nguyên tắc sàng lọc tính khả thi và bổ sung bằng chứng thực nghiệm, nhưng không sử dụng nguyên bộ đặc tính DBMS hoặc cơ chế tổng hợp có trọng số của nghiên cứu này. [[2]](https://siamakfarshidi.nl/publications/DBMS.pdf)

ATAM cung cấp cách mô tả kịch bản thông qua tác nhân kích thích, môi trường và phản ứng có thể quan sát, đồng thời phân tích rủi ro và đánh đổi giữa các thuộc tính chất lượng. Đề tài sử dụng cách tư duy này để chuyển những yêu cầu như “hỗ trợ ghi đồng thời” hoặc “phục hồi được sau sự cố” thành các tình huống kiểm tra cụ thể. Đây là sự vận dụng một phần cách phân tích theo kịch bản, không phải thực hiện đầy đủ quy trình ATAM. [[3]](https://sei.cmu.edu/documents/629/2000_005_001_13706.pdf)

Roy và Słowiński cho thấy việc chọn phương pháp hỗ trợ quyết định đa tiêu chí cần xét mục tiêu quyết định, tính chất dữ liệu, mô hình sở thích và mức độ chấp nhận bù trừ. Theo đó, việc chưa có trọng số không đồng nghĩa với việc không thể ra quyết định; đồng thời, ưu tiên diễn đạt bằng lời vẫn chứa lựa chọn chủ quan cần được công khai. [[4]](https://link.springer.com/article/10.1007/s40070-013-0004-7)

### 2.2. Lựa chọn phương pháp chính và phần điều chỉnh của đề tài

Đề tài lựa chọn **lọc điều kiện bắt buộc kết hợp phân tích kịch bản và đánh đổi dựa trên bằng chứng** làm phương pháp chính. Lý do là dữ liệu đầu vào có nhiều dạng khác nhau: khả năng tích hợp có thể được xác nhận bằng kiểm thử; hiệu năng được đo bằng đại lượng định lượng; trách nhiệm quản lý metadata cần mô tả kiến trúc; còn rủi ro vận hành hoặc migration cần phân tích theo điều kiện sử dụng. Giữ các dạng bằng chứng này giúp giải thích quyết định mà chưa cần đặt ra thang điểm chung.

AHP, TOPSIS hoặc mô hình giá trị có trọng số chưa được chọn làm thành phần mặc định. Việc bổ sung một phương pháp đa tiêu chí chỉ được xem xét khi có nhu cầu tổng hợp rõ ràng, dữ liệu phù hợp và người quyết định có thể xác nhận các giả định về thang đo, sở thích và sự bù trừ. Đối với mô hình giá trị cộng, còn phải xem xét sự phụ thuộc giữa các tiêu chí và nguy cơ tính lặp một lợi ích. Dù bổ sung mô hình nào, yêu cầu bắt buộc vẫn được kiểm tra trước, không được bù bằng điểm thuận lợi ở tiêu chí khác. Đây là lựa chọn thiết kế của đề tài theo bối cảnh hiện có, không phải kết luận rằng phương pháp chính luôn tốt hơn các phương pháp đa tiêu chí khác.

Các điều chỉnh riêng cho catalog gồm: xác định đơn vị đánh giá theo cấu hình triển khai; ánh xạ yêu cầu vào các trách nhiệm metadata; tách chức năng chung khỏi chức năng riêng; quy định cách xử lý thiếu bằng chứng; và xây dựng các kịch bản đọc metadata, commit, quan sát cập nhật, xử lý xung đột, phục hồi và migration. Danh mục tiêu chí, quy tắc trạng thái, mẫu hồ sơ quyết định và thiết kế benchmark là các đề xuất của đề tài. Chúng chưa được kiểm chứng độc lập và không được xem là kết quả đã được các nguồn trên xác nhận.

## 3. Đầu vào của quá trình lựa chọn

Đầu vào đầu tiên là hồ sơ bài toán, xác định lựa chọn catalog phục vụ xây dựng hệ thống mới hay thay thế hệ thống hiện có, ai sử dụng kết quả và quyết định cần đạt đến mức nào. Khuyến nghị để tiếp tục thử nghiệm có yêu cầu bằng chứng khác với khuyến nghị triển khai thực tế.

Các nhóm thông tin cần thu thập được trình bày trong Bảng 1.

**Bảng 1. Thông tin đầu vào cần xác định**

| Nhóm thông tin | Nội dung cần thu thập | Vai trò trong quyết định |
|---|---|---|
| Mục tiêu và phạm vi | Bài toán sử dụng, hệ thống mới hoặc hiện có, người xác nhận yêu cầu, thời hạn và phạm vi quyết định | Xác định câu hỏi lựa chọn và giới hạn khuyến nghị |
| Tích hợp | Engine, client, phiên bản, table format, storage, giao diện và các thao tác cần thực hiện | Xác định đường tích hợp cần kiểm chứng |
| Quy mô và tải | Số bảng, namespace, kích thước metadata, số snapshot, tần suất thao tác, phân bố truy cập và số writer đồng thời | Xây dựng workload và điều kiện đo có liên quan |
| Mức dịch vụ và ràng buộc | Độ trễ, khả dụng, phục hồi, bảo mật, vị trí dữ liệu, mô hình triển khai, giấy phép và ngân sách nếu có | Xác định điều kiện bắt buộc và ngưỡng chấp nhận |
| Vận hành và vòng đời | Nhân sự, công cụ giám sát, hỗ trợ, nâng cấp, hệ thống nguồn, migration và khả năng chuyển ra khỏi nền tảng | Đánh giá công triển khai, rủi ro và chi phí vòng đời |
| Mục tiêu ưu tiên | Những lợi ích mong muốn, mức cải thiện có ý nghĩa và đánh đổi chấp nhận được | Phân biệt các phương án đã đáp ứng điều kiện bắt buộc |

Mỗi yêu cầu được gán mã và lưu nguồn, người xác nhận, trạng thái xác nhận, phạm vi áp dụng, điều kiện chấp nhận cùng bằng chứng cần có. Ngưỡng định lượng phải xuất phát từ yêu cầu được xác nhận hoặc từ phép dẫn xuất có giải thích và được chấp thuận. Tham số được chọn để thử bộ đo không được sử dụng thay cho yêu cầu hệ thống.

Nếu chưa có dữ liệu thực tế, có thể xây dựng ca nghiên cứu giả định, nhưng phải ghi rõ những giả định về workload, hạ tầng và ưu tiên. Kết quả của ca này chỉ có ý nghĩa minh họa cách áp dụng phương pháp. Việc thiếu yêu cầu không được diễn giải thành mọi phương án đều phù hợp.

## 4. Tiêu chí và điều kiện bắt buộc

### 4.1. Danh mục nhóm tiêu chí

Tám nhóm kỹ thuật ban đầu được giữ làm cơ sở mô tả. Để hỗ trợ quyết định, các nhóm rộng được tách thành những nội dung có cách kiểm chứng khác nhau; đồng thời bổ sung vận hành, chi phí, migration và độ trưởng thành. Kết quả là 15 nhóm rà soát trong Bảng 2. Đây là danh mục định hướng thu thập thông tin, chưa phải 15 tiêu chí độc lập hoặc một bộ tiêu chí đã được chứng minh đầy đủ cho mọi hệ thống.

**Bảng 2. Nhóm tiêu chí và bằng chứng đánh giá**

| Mã | Nhóm tiêu chí | Câu hỏi đối với quyết định | Bằng chứng và cách kiểm chứng dự kiến |
|---|---|---|---|
| C01 | Mô hình đối tượng | Các đối tượng và thao tác của hệ thống có biểu diễn được không? | Mô hình namespace, table, view hoặc branch; tài liệu giới hạn; kiểm thử các thao tác cần dùng |
| C02 | Trách nhiệm quản lý metadata | Thành phần nào sở hữu trạng thái, công bố cập nhật, quản lý lịch sử và thực hiện cleanup? | Sơ đồ luồng và phân công trách nhiệm; tài liệu vòng đời; kiểm thử lifecycle khi liên quan |
| C03 | Giao diện, giao thức và client | Đường tích hợp cần thiết có hoạt động với đúng bộ phiên bản không? | Đặc tả API, ma trận tương thích, cấu hình hiệu lực và trace kiểm thử |
| C04 | Xác thực | Có đáp ứng cơ chế danh tính và vòng đời thông tin xác thực được yêu cầu không? | Luồng xác thực; kiểm thử token hợp lệ, không hợp lệ, hết hạn và refresh khi cần |
| C05 | Phân quyền và audit | Quyền có được thực thi đúng trên tài nguyên, thao tác và chủ thể liên quan không? | Ma trận quyền; kiểm thử cho phép, từ chối, thu hồi quyền và bản ghi audit |
| C06 | Commit, concurrency và consistency | Cập nhật được công bố, quan sát và xử lý xung đột theo ngữ nghĩa nào? | Hợp đồng hành vi; lịch sử request và phản hồi; kiểm thử commit, visibility, xung đột và trạng thái chưa rõ |
| C07 | Persistence và phục hồi | Trạng thái nào được bảo toàn và có thể khôi phục trong các tình huống lỗi cần xét? | Thiết kế lưu trạng thái; quy trình backup/restore; kiểm thử phục hồi theo loại lỗi xác định |
| C08 | Hiệu năng và khả năng mở rộng | Cấu hình có đáp ứng tải metadata và mức dịch vụ yêu cầu không? | Benchmark độ trễ, lượng thao tác thành công, lỗi và tài nguyên tại tải, quy mô xác định |
| C09 | Quản lý truy cập storage | Quyền truy cập dữ liệu có phù hợp mô hình tin cậy và phạm vi truy cập không? | Sơ đồ đường truy cập; chính sách storage; kiểm thử phạm vi credentials, hết hạn và các đường truy cập trực tiếp |
| C10 | Table format và interoperability | Những tổ hợp engine–format–thao tác cần thiết có hoạt động đúng không? | Ma trận đọc/ghi/DDL theo phiên bản; kiểm thử dữ liệu, schema và snapshot qua đường tích hợp thực tế |
| C11 | Federation và phạm vi quản lý | Có cần quản lý nhiều nguồn hoặc backend và cấu hình nào đáp ứng được nhu cầu đó? | Sơ đồ connector và backend; kiểm thử chuyển tiếp quyền, đồng bộ và ảnh hưởng của tầng federation |
| C12 | Vận hành và quan sát | Đội ngũ có thể triển khai, giám sát, nâng cấp và xử lý sự cố không? | Runbook, metrics, log; diễn tập thao tác; nhật ký công việc và thời gian thực hiện |
| C13 | Chi phí vòng đời | Chi phí có nằm trong ngân sách và được so sánh trên cùng mức dịch vụ không? | Hạng mục tài nguyên, dịch vụ, nhân công, chuyển đổi; đơn giá có nguồn và ước tính theo kịch bản |
| C14 | Migration và khả năng chuyển đổi | Có thể chuyển hệ thống, bảo toàn thuộc tính cần thiết và xử lý rollback không? | Quy trình chuyển; kiểm thử trên bản sao; đối chiếu dữ liệu, metadata, quyền, downtime và công thực hiện |
| C15 | Độ trưởng thành và hỗ trợ | Phiên bản và đường tích hợp có đáp ứng yêu cầu về hỗ trợ, bảo trì và giấy phép không? | Release notes, trạng thái tính năng, tài liệu nâng cấp, vấn đề liên quan và phương án hỗ trợ |

Từng nhóm chỉ được chuyển thành tiêu chí đánh giá khi liên quan đến bài toán. Chẳng hạn, branch hoặc federation có thể là điều kiện quyết định trong một workflow cụ thể, nhưng không được tự động tính là ưu thế khi hệ thống không cần chức năng đó. Ngược lại, nếu chức năng riêng tạo ra lý do lựa chọn, phải có kịch bản đánh giá riêng; bộ thao tác chung không được dùng để loại bỏ giá trị này khỏi phân tích.

### 4.2. Phân loại và quy tắc trạng thái

Mỗi tiêu chí cụ thể được phân thành ba loại. **Điều kiện bắt buộc (B)** là điều kiện không thể đánh đổi, có nguồn và lý do rõ ràng. **Mục tiêu ưu tiên (U)** là lợi ích dùng để so sánh các phương án đã đáp ứng yêu cầu tối thiểu. **Thông tin bối cảnh (I)** giúp giải thích kiến trúc hoặc rủi ro nhưng chưa trực tiếp quyết định loại hay chọn phương án. Một đặc tính có thể đồng thời có mức tối thiểu bắt buộc và mục tiêu cải thiện; hai nội dung này cần được ghi thành các điều kiện riêng.

Trạng thái đánh giá gồm: **đạt (PASS)**, **không đạt (FAIL)**, **chưa xác minh (UNKNOWN)** và **không áp dụng (N/A)**. PASS chỉ có nghĩa là đáp ứng điều kiện trong phạm vi và mức bằng chứng đã quy định. N/A cần có lý do ngoài phạm vi; không dùng trạng thái này để thay cho thiếu dữ liệu hoặc thiếu chức năng cần thiết.

Phương án có một điều kiện B không đạt bị loại khỏi danh sách đủ điều kiện của ca đang xét. Phương án còn B chưa xác minh được giữ trong danh sách cần bổ sung bằng chứng, chưa được khuyến nghị triển khai. Chỉ khi các B đều đạt theo mức bằng chứng đã thống nhất mới chuyển sang phân tích ưu tiên. Nếu sửa cấu hình để đáp ứng một điều kiện, phải ghi phiên bản cấu hình mới và đánh giá lại các kết luận bị ảnh hưởng.

Đối với U chưa có dữ liệu, giữ trạng thái thiếu thông tin, sử dụng khoảng có căn cứ hoặc phân tích các kịch bản. Không tự gán điểm bằng không, giá trị trung bình hoặc mức phạt. Nếu dữ liệu thiếu có khả năng làm đổi khuyến nghị, cần bổ sung bằng chứng hoặc thu hẹp kết luận.

### 4.3. Tránh trùng lặp và rà soát phần còn thiếu

Mỗi kết quả quan sát có một nhóm tiêu chí chính và có thể liên kết tới các nhóm liên quan. Ví dụ, thời gian commit được ghi ở C08, còn tính đúng đắn của commit được ghi ở C06; cùng một lợi ích hiệu năng không được tính hai lần. Tương tự, công migration được mô tả tại C14 và có thể dùng để tính chi phí tại C13, nhưng một công việc chỉ được tính tiền một lần. Nếu cả chi phí nhân công và số giờ công được giữ làm mục tiêu ưu tiên, cần giải thích thêm ràng buộc nhân lực khiến cả hai cùng có ý nghĩa.

Khi rà soát yêu cầu, cần hỏi thêm về khả năng nhìn thấy cập nhật sau commit, cách ly giữa các tenant, bảo vệ metadata, vòng đời secrets và các thao tác DDL hoặc cleanup đồng thời. Những nội dung này chỉ trở thành điều kiện bắt buộc khi được bài toán yêu cầu. Thử nghiệm append trên một bảng không thay thế kiểm chứng cho các workflow khác.

## 5. Quy trình đánh giá

### 5.1. Xác lập bài toán và kế hoạch bằng chứng

Trước khi đánh giá sản phẩm, xác nhận mục tiêu, phạm vi chức năng, ràng buộc và các đánh đổi còn mở. Với mỗi B, xác định loại bằng chứng đủ để chấp nhận: tài liệu có thể phù hợp để xác nhận giấy phép; còn đường tích hợp hoặc hành vi khi lỗi có thể cần kiểm thử. Các ngưỡng, quy tắc ưu tiên và điều kiện chấp nhận được ghi trước khi xem kết quả so sánh.

Sản phẩm của bước này là hồ sơ yêu cầu và kế hoạch kiểm chứng. Bước chỉ hoàn thành khi mỗi B có nguồn, phạm vi, cách kiểm tra và trạng thái xác nhận; nếu là ca giả định, toàn bộ giả định phải được nhận diện.

### 5.2. Sàng lọc tài liệu và xác định cấu hình ứng viên

Sáu công nghệ được rà soát theo cùng chuẩn bằng chứng, ưu tiên tài liệu chính thức đúng phiên bản và đúng đường tích hợp. Mỗi nhận định phải nêu cấu hình mà nó áp dụng. Tài liệu không đề cập một khả năng chưa đủ để kết luận sản phẩm không hỗ trợ; trường hợp đó thường cần giữ UNKNOWN và tìm bằng chứng bổ sung.

Kết quả sàng lọc phân biệt ba vấn đề: phù hợp về chức năng theo bằng chứng hiện có; có thể triển khai trong phòng thí nghiệm; và được chọn vào mẫu nghiên cứu. Không được đo vì thiếu thời gian hoặc tài nguyên không có nghĩa là không phù hợp. Từ kết quả này, dự kiến chọn hai cấu hình để thực nghiệm; chỉ thêm cấu hình thứ ba khi nó giúp làm rõ một đánh đổi quan trọng.

### 5.3. Xác định khả năng so sánh và khóa kế hoạch thực nghiệm

Trước khi so sánh hiệu năng, lập bảng hành vi cần đáp ứng cho từng thao tác: phạm vi giao dịch, tính bền vững, khả năng quan sát cập nhật, quy tắc xung đột, retry, quyền và trách nhiệm metadata. Các phương án chỉ được đặt trong cùng phép so hiệu năng trực tiếp khi thao tác và các bảo đảm cần thiết tương đương trong phạm vi câu hỏi nghiên cứu.

Nếu một phương án có thêm tầng federation, dịch vụ chính sách hoặc phạm vi giao dịch khác, khác biệt đó phải được thể hiện như một đánh đổi kiến trúc. Có thể thiết kế phép đo riêng cho phần chức năng chung và cho chức năng bổ sung. Không gộp tất cả vào một bảng tốc độ rồi quy chênh lệch cho tên sản phẩm.

Sau khi khảo sát thử bộ đo, kế hoạch thực nghiệm chính thức sẽ được khóa, gồm cấu hình, workload, phép kiểm tra tính đúng đắn, chỉ số chính, số lần lặp, quy tắc dừng, xử lý lỗi và cách phân tích. Những nội dung này hiện là kế hoạch cần hoàn thiện trước khi chạy.

### 5.4. Thu thập, đối chiếu và cập nhật trạng thái

Bằng chứng tài liệu, kiểm thử, benchmark và ước tính chi phí được gắn với cùng mã yêu cầu và mã phương án. Khi nguồn mâu thuẫn, cần xác định khác biệt về phiên bản, cấu hình hoặc thao tác, sau đó kiểm thử phân giải nếu phù hợp. Không chọn riêng nguồn thuận lợi cho một ứng viên.

Một lỗi quan sát được phải được điều tra để phân biệt lỗi bộ đo, client, cấu hình, catalog hoặc thành phần phụ thuộc. Lỗi chưa phân giải không được biến thành bằng chứng xác định về chất lượng sản phẩm. Sau mỗi đợt bổ sung bằng chứng, cập nhật trạng thái điều kiện và ghi rõ lý do thay đổi.

### 5.5. Phân tích đánh đổi và kiểm tra độ nhạy

Các phương án đủ điều kiện được so sánh trên các U có liên quan, giữ đơn vị gốc như độ trễ, giờ công, chi phí và những mô tả định tính có căn cứ. Có thể nhận diện quan hệ trội Pareto khi một phương án không kém trên mọi chiều đang xét và tốt hơn trên ít nhất một chiều. Chỉ sử dụng quan hệ này khi dữ liệu đủ để so sánh; không ép thứ tự cho tiêu chí định tính chưa có quy tắc hoặc cho các khoảng bất định chưa phân biệt được.

Nếu còn nhiều phương án, sử dụng ưu tiên đã được xác nhận để giải thích đánh đổi. Khi chưa có ưu tiên đủ rõ, giữ danh sách phương án và nêu thông tin nào cần bổ sung để phân biệt chúng. Số lượng tính năng không được dùng làm quy tắc mặc định để chọn phương án thắng.

Cuối cùng, thay đổi các yếu tố có thể ảnh hưởng quyết định trong phạm vi có căn cứ, chẳng hạn tải metadata, chi phí nhân công, yêu cầu migration hoặc thứ tự ưu tiên. Ghi nhận những trường hợp khuyến nghị giữ nguyên và những điều kiện khiến nó thay đổi. Không đặt phân phối xác suất cho các giả định khi chưa có dữ liệu hỗ trợ.

## 6. Sử dụng bằng chứng và benchmark

### 6.1. Hồ sơ bằng chứng và khả năng truy vết

Mỗi bằng chứng cần có mã, nguồn hoặc dữ liệu gốc, ngày thu thập, phiên bản, cấu hình, thao tác, điều kiện quan sát, kết luận hỗ trợ và giới hạn. Chuỗi truy vết của một nhận định là: **yêu cầu → tiêu chí cụ thể → cách kiểm chứng → bằng chứng → trạng thái → ảnh hưởng đến quyết định**.

Ví dụ minh họa về cấu trúc truy vết, chưa phải kết quả thử nghiệm: nếu ca nghiên cứu yêu cầu một reader độc lập nhìn thấy cập nhật sau khi writer nhận xác nhận commit, yêu cầu đó được ánh xạ vào C06. Kịch bản kiểm tra sẽ phối hợp writer và reader, ghi phản hồi commit, lần đọc và dữ liệu quan sát. Điều kiện chấp nhận phải dựa trên yêu cầu visibility đã xác nhận. Nếu chưa có điều kiện này, phép thử chỉ tạo quan sát, chưa đủ cơ sở gán PASS.

Đề tài không gom chất lượng bằng chứng thành một điểm tin cậy duy nhất. Thay vào đó, hồ sơ ghi loại bằng chứng, mức phù hợp với ca, phạm vi được bao phủ, tình trạng lặp lại hoặc rà soát, nguồn mâu thuẫn và bất định còn lại. Bằng chứng thực nghiệm không mặc nhiên phù hợp hơn tài liệu cho mọi nhận định; chẳng hạn, thử nghiệm không thay thế căn cứ về giấy phép.

### 6.2. Vai trò và cấu trúc benchmark

Benchmark có nhiệm vụ làm rõ những bất định có thể thay đổi việc đáp ứng yêu cầu, đánh đổi hoặc mức chắc chắn của khuyến nghị. Trước mỗi phép đo, cần nêu câu hỏi mà kết quả dự kiến trả lời. Việc kết quả đo không làm thay đổi khuyến nghị vẫn là một kết quả nghiên cứu hợp lệ.

Cách tách mô tả workload khỏi phần kết nối hệ thống tham khảo thiết kế YCSB. Tuy nhiên, workload key–value của YCSB không được sử dụng nguyên trạng làm workload catalog. Đề tài sẽ xây dựng thao tác và kiểm tra riêng cho metadata, commit, visibility và quyền truy cập. [[5]](https://cgi.di.uoa.gr/~ad/M155/Papers/p143-cooper.pdf)

Bảng 3 trình bày bộ kịch bản dự kiến. Bộ lõi cho ca đọc/ghi bảng gồm B0, B1, B1V và B2. Các kịch bản còn lại trở thành bắt buộc khi yêu cầu tương ứng có trong ca; thiếu thời gian không phải lý do đổi một yêu cầu bắt buộc thành mục tiêu ưu tiên.

**Bảng 3. Kế hoạch kiểm thử và benchmark theo câu hỏi quyết định**

| Mã và kịch bản | Thiết kế workload và cấu hình dự kiến | Chỉ số, kiểm tra tính đúng đắn và vai trò quyết định |
|---|---|---|
| B0 — Tích hợp và quyền | Dùng engine/client thực với các vai trò được phép và không được phép; thực hiện thao tác đối tượng, đọc/ghi, xác thực và truy cập storage thuộc yêu cầu | Đối chiếu dữ liệu, schema và hiệu ứng thao tác; kiểm tra cả cho phép và từ chối. Là điều kiện chức năng trước khi diễn giải hiệu năng |
| B1 — Đọc metadata | Fixture metadata cố định, không có writer; thay đổi tải load/list theo kế hoạch; khóa chính sách cache và xác nhận request thực | Đo độ trễ, thao tác thành công, lỗi, hàng đợi và tài nguyên; kiểm tra phản hồi đúng fixture. Cung cấp bằng chứng đáp ứng tải trong cấu hình đã đo |
| B1V — Quan sát cập nhật | Writer công bố dữ liệu có mã nhận diện; sau xác nhận commit, reader độc lập đọc theo thứ tự được điều phối; kiểm tra đường đọc mới và cache nếu cần | Ghi lần đọc còn cũ, thời gian quan sát cập nhật và thao tác chưa phân giải. So với hợp đồng visibility, không suy thành kiểm chứng mọi lịch sử đồng thời |
| B2 — Commit không tranh chấp | Cùng số bảng, trạng thái ban đầu, tổng thao tác và kích thước dữ liệu; thay số writer, mỗi bảng chỉ có một writer tại một thời điểm | Đo độ trễ attempt và thao tác logic, goodput, retry và lỗi; đối chiếu lịch sử công bố với dữ liệu cuối. Đánh giá commit dưới cùng bảo đảm dữ liệu |
| B3 — Ghi đồng thời | Writer cùng cập nhật một bảng; tách kiểm tra điều kiện cập nhật nghiêm ngặt khỏi workload append có retry; giữ tổng số thao tác cố định giữa các mức concurrency | Ghi xung đột, retry, thao tác thành công và chưa rõ kết quả; kiểm tra cập nhật đã xác nhận, dữ liệu lặp hoặc ngoài dự kiến. Phân biệt xung đột hợp lệ với vi phạm tính đúng đắn |
| B4 — Lỗi và phục hồi | Chọn trước loại lỗi liên quan, thời điểm kích hoạt theo dấu mốc thao tác; tách dừng tiến trình khỏi mất phản hồi; giữ rõ phạm vi backend/storage chịu lỗi | Kiểm tra dữ liệu đã xác nhận còn đọc được; ghi khoảng thời điểm chức năng phục hồi và thao tác chưa phân giải. Chỉ hỗ trợ kết luận cho loại lỗi được thử |
| B5 — Migration | Thử một cặp nguồn–đích trên bản sao dữ liệu; kiểm kê, dừng writer, chuyển đổi, xác minh, đọc/ghi ở đích; xét rollback trước và sau khi có ghi mới | Đối chiếu dữ liệu, metadata và quyền cần bảo toàn; ghi downtime, công thực hiện và đối tượng không chuyển được. Hỗ trợ đánh giá phương án migration cụ thể |

Nếu branch, federation hoặc một chức năng riêng là lý do lựa chọn, kế hoạch sẽ bổ sung kịch bản tương ứng. Kết quả của các thao tác chung không đại diện cho toàn bộ phạm vi chức năng của sản phẩm.

### 6.3. Kiểm soát cấu hình và ranh giới phép đo

Mỗi lượt chạy sẽ lưu bản mô tả môi trường gồm phiên bản hoặc image digest, backend, engine/client, table format, storage, tài nguyên, cấu hình quyền, network, timeout, retry và dữ liệu ban đầu. Khi khả thi, các phương án sử dụng cùng client, fixture tương đương, cùng loại storage và điều kiện mạng. Những khác biệt không thể đồng nhất phải được ghi và đưa vào diễn giải.

Ba loại thời gian được tách riêng. Độ trễ một lần gọi API được đo từ lúc client gửi request đến khi nhận đủ phản hồi; nó có thể bao gồm mạng, xác thực, catalog, backend và truy cập storage. Độ trễ thao tác metadata logic bao gồm các attempt, refresh, retry hoặc backoff cần thiết. Thời gian truy vấn toàn bộ engine chỉ dùng cho đánh giá tích hợp hoặc được báo riêng. Không sử dụng toàn bộ thời gian truy vấn để quy kết hiệu năng riêng của catalog.

Đối với commit, thời gian chuẩn bị và ghi file dữ liệu hoặc manifest ở client cần được phân biệt với giai đoạn công bố cập nhật. Tuy vậy, nếu đường công bố có I/O tới storage thì độ trễ quan sát vẫn chứa phần công việc đó. Không suy ra thời gian xử lý thuần của catalog bằng cách trừ các số đo không cùng điều kiện.

Trạng thái cache được kiểm soát bằng quy trình khởi tạo và làm nóng đã xác định từ giai đoạn khảo sát thử. Khởi động lại tiến trình không mặc nhiên làm lạnh mọi cache. Dữ liệu ban đầu được khôi phục giữa các lượt chạy để tránh chênh lệch do metadata tăng trưởng. CPU, bộ nhớ, I/O, cơ sở dữ liệu và bộ phát tải được giám sát để phát hiện giới hạn ngoài catalog. Cùng hạn mức tài nguyên không đủ chứng minh chênh lệch chỉ do mã nguồn catalog; một quy mô đo cũng chưa chứng minh khả năng mở rộng.

### 6.4. Tính đúng đắn, phép lặp và diễn giải số liệu

Bộ phát tải và bộ kiểm tra kết quả sẽ được kiểm chứng trước khi dùng để đánh giá sản phẩm. Kế hoạch bao gồm dữ liệu thử hợp lệ và dữ liệu được cấy lỗi có chủ đích, như thiếu bản ghi đã xác nhận, bản ghi lặp hoặc phản hồi cũ. Lịch sử thao tác phải phân biệt thành công, từ chối chắc chắn, xung đột hợp lệ và kết quả chưa rõ. Timeout không tự chứng minh giao dịch đã bị hủy.

Trong bài append-only, việc kiểm tra sẽ đối chiếu dữ liệu ban đầu, dữ liệu của các thao tác đã được xác nhận, các thao tác chắc chắn không được công bố và các thao tác chưa phân giải với dữ liệu thực tế. Khi còn thao tác chưa rõ kết quả, không được tự coi chúng là mất dữ liệu hoặc không thành công. Bản ghi lặp cũng cần được điều tra để phân biệt retry ở client với hành vi của server.

Elle cho thấy việc suy luận bất thường giao dịch từ lịch sử quan sát phụ thuộc vào mô hình và khả năng thu hồi thông tin cần thiết từ lịch sử đó. Vì vậy, bộ kiểm tra tùy biến của đề tài không thừa hưởng bảo đảm của Elle; trạng thái dữ liệu cuối đúng chưa đủ chứng minh linearizability hoặc mọi mức cô lập. Các phép thử chỉ xác nhận hoặc tìm phản ví dụ cho thuộc tính và lịch sử nằm trong phạm vi thiết kế. [[6]](https://www.vldb.org/pvldb/vol14/p268-alvaro.pdf)

Kế hoạch đo gồm giai đoạn khảo sát thử, khóa kế hoạch và thu thập dữ liệu mới cho lượt đo chính thức. Khảo sát thử dùng để kiểm tra khả năng phát tải, trạng thái làm nóng, nguồn biến thiên và ngân sách đo. Số lần lặp phải được xác định theo yêu cầu phân tích và biến thiên quan sát, không mặc định một số nhỏ lượt chạy là đủ. Nguyên tắc này tham khảo Kalibera và Jones; các kỹ thuật trong nghiên cứu gốc không được chuyển trực tiếp thành cách tính khoảng tin cậy cho p95 độ trễ request. [[7]](https://kar.kent.ac.uk/33611/)

Mỗi lượt chạy sẽ báo số thao tác được lên lịch, số được gửi, số thành công, bị từ chối, timeout và chưa rõ kết quả. Goodput chỉ đếm thao tác logic thành công hữu ích, không cộng retry như công việc mới. Với cửa sổ đo cố định, thao tác hoàn tất muộn được báo riêng; với lô công việc cố định, thời gian hoàn thành lô phải được nêu rõ. Các phân vị độ trễ luôn kèm quần thể tính toán; p95 của những request thành công không được gọi là p95 của mọi request khi đã loại timeout.

Nếu chỉ đủ dữ liệu mô tả, đề tài sẽ báo kết quả từng lượt và mức biến thiên, không gán khoảng tin cậy thống kê. Khi cần kiểm tra một SLO chính thức, phải xác định trước đại lượng ước lượng, đơn vị lấy mẫu, xử lý phụ thuộc và timeout, cùng quy tắc chấp nhận. Nếu dữ liệu chưa phân biệt được với ngưỡng, trạng thái vẫn là UNKNOWN. Việc công bố cấu hình, đơn vị, biến thiên và tránh chỉ chọn kết quả thuận lợi tham khảo các nguyên tắc báo cáo benchmark của Hoefler và Belli. [[8]](https://htor.inf.ethz.ch/publications/img/hoefler-scientific-benchmarking.pdf)

### 6.5. Bằng chứng chi phí và hiệu quả kinh tế

Phân tích chi phí sẽ sử dụng cùng kỳ đánh giá và cùng phạm vi dịch vụ, gồm các hạng mục liên quan như triển khai, migration, hạ tầng, dịch vụ, vận hành, hỗ trợ và chuyển đổi ra khỏi hệ thống. Những yêu cầu về dự phòng, backup hoặc trực vận hành, nếu có, phải được tính nhất quán giữa các phương án. Phần mềm nguồn mở không đồng nghĩa với tổng chi phí bằng không.

Nhật ký thực nghiệm sẽ tách thời gian máy chạy, thời gian thao tác của người thực hiện, thời gian học ban đầu và công việc có thể lặp lại. Mỗi công việc chỉ được tính một lần khi quy đổi thành chi phí. Nếu chưa có đơn giá, giữ các đại lượng tài nguyên và giờ công. Nếu chưa có tải thực tế được xác nhận, không ngoại suy trực tiếp số request trong lab thành chi phí vận hành năm.

Ba loại thông tin kinh tế được phân biệt: tài nguyên và công sức quan sát trong lab; ước tính chi phí theo kịch bản có giả định và đơn giá; hiệu quả thực tế so với phương án cơ sở trên cùng phạm vi dịch vụ. Chỉ loại thứ ba, với bằng chứng phù hợp, mới hỗ trợ nhận định về hiệu quả kinh tế đã đạt. Hiện đề tài chưa có số liệu cho các kết luận này. Tỷ trọng chấm điểm cuộc thi không được dùng làm trọng số lựa chọn catalog.

## 7. Hình thành khuyến nghị và kiểm chứng phương pháp

### 7.1. Nội dung hồ sơ khuyến nghị

Đầu ra của quá trình lựa chọn là hồ sơ quyết định, gồm câu hỏi lựa chọn và phiên bản yêu cầu; danh sách cấu hình đủ điều kiện; danh sách không đạt cùng lý do; danh sách cần xác minh; phương án được khuyến nghị hoặc tập phương án còn phù hợp; các đánh đổi; bằng chứng hỗ trợ; và điều kiện làm thay đổi khuyến nghị.

Khuyến nghị cần được diễn đạt theo phạm vi áp dụng, chẳng hạn: cấu hình nào phù hợp với những yêu cầu đã xác nhận, dựa trên những phép kiểm chứng nào và còn phụ thuộc giả định gì. Không chuyển kết quả này thành tuyên bố một catalog tốt nhất trong mọi bối cảnh. Nếu chưa có đủ dữ liệu hoặc sở thích để phân biệt các phương án, đầu ra hợp lệ là danh sách lựa chọn kèm các câu hỏi cần giải quyết tiếp.

Mức chắc chắn được mô tả bằng ba trạng thái:

- **Chưa kết luận:** còn điều kiện bắt buộc chưa xác minh hoặc chưa đủ dữ liệu và ưu tiên để hình thành khuyến nghị lựa chọn.
- **Có điều kiện:** các điều kiện bắt buộc đạt mức bằng chứng đã thống nhất, nhưng khuyến nghị còn phụ thuộc những giả định hoặc ước tính được nêu rõ.
- **Có bằng chứng trực tiếp và ổn định trong các kịch bản đã xét:** các kết luận quan trọng có bằng chứng phù hợp, ưu tiên được xác nhận và khuyến nghị giữ nguyên qua các biến thể đã kiểm tra.

Các trạng thái này là mô tả hồ sơ bằng chứng và độ ổn định của quyết định, không phải xác suất hoặc mức tin cậy thống kê. Một kết quả hiệu năng thuận lợi không khắc phục được thiếu bằng chứng về điều kiện bắt buộc khác. Mức chắc chắn của phép đọc metadata cũng không tự truyền sang commit đồng thời, phục hồi hoặc migration.

### 7.2. Kế hoạch kiểm chứng tính hữu ích của phương pháp

Benchmark cung cấp bằng chứng về cấu hình, chưa đủ kiểm chứng chất lượng của chính quy trình lựa chọn. Đề tài dự kiến áp dụng phương pháp cho một ca có yêu cầu được xác nhận và ít nhất một biến thể quan trọng, sau đó cung cấp cùng hồ sơ bằng chứng cho người rà soát để tái dựng quyết định. Các nội dung ghi nhận gồm khả năng truy vết kết luận, bất đồng khi phân loại yêu cầu, thời gian áp dụng và ảnh hưởng của bằng chứng bổ sung. Đồng thuận giữa người đánh giá không được xem là bằng chứng lựa chọn tối ưu.

Các kiểm tra logic dự kiến gồm: phương án có B không đạt không được vào danh sách đủ điều kiện; B chưa xác minh không được chuyển thành đạt nếu không có bằng chứng; kết quả bị ghi lặp không tạo thêm lợi ích; và thay đổi phiên bản phải dẫn đến rà soát các kết luận bị ảnh hưởng. Những kiểm tra này chưa được thực hiện.

Nếu muốn đánh giá phương pháp có cải thiện so với cách dùng bảng so sánh tính năng thông thường hay không, cần có phương án cơ sở sử dụng cùng yêu cầu và bằng chứng, đồng thời kiểm soát ảnh hưởng của thứ tự đánh giá và kinh nghiệm người thực hiện. Khi chưa có thiết kế đối chứng phù hợp, kết quả chỉ được trình bày như một nghiên cứu tình huống về khả năng áp dụng.

## 8. Giới hạn của phương pháp

Thứ nhất, danh mục 15 nhóm tiêu chí và các quy tắc xử lý là sự điều chỉnh cho phạm vi đề tài, chưa được kiểm chứng về tính đầy đủ hoặc khả năng khái quát. Một hệ thống có yêu cầu đặc thù có thể cần thêm tiêu chí và phép kiểm tra.

Thứ hai, việc xác định điều kiện bắt buộc, ưu tiên và mức đánh đổi vẫn phụ thuộc vào người xác nhận yêu cầu. Công khai nguồn và giả định giúp kiểm tra quyết định nhưng không loại bỏ hoàn toàn tính chủ quan. Khi chưa có hồ sơ thực tế, khuyến nghị chỉ áp dụng cho ca giả định.

Thứ ba, kết quả thực nghiệm sau này sẽ bị giới hạn bởi phiên bản, cấu hình, workload, tài nguyên và môi trường đã thử. Bộ thao tác chung không bao phủ mọi chức năng riêng; so sánh dịch vụ được quản lý với hệ thống tự vận hành cần xét thêm khác biệt phạm vi dịch vụ. Những công nghệ không được đưa vào lab không vì vậy mà bị xem là không phù hợp.

Thứ tư, thử nghiệm hữu hạn có thể phát hiện phản ví dụ nhưng không bảo đảm không còn lỗi. Kiểm tra read-after-write không chứng minh mọi thuộc tính nhất quán; restart tiến trình không thay cho kiểm thử backup, failover hoặc khôi phục thảm họa. Các kết luận hiệu năng và tính đúng đắn phải giới hạn theo những điều kiện đã quan sát.

Thứ năm, quy mô mẫu và khả năng đo bất định có thể bị giới hạn bởi nguồn lực sinh viên. Nếu chưa đủ dữ liệu cho suy luận thống kê hoặc kiểm tra ngưỡng dịch vụ, kết quả cần được giữ ở mức mô tả hoặc chưa kết luận. Không tăng độ chắc chắn bằng cách bỏ các lượt thất bại hay chỉ chọn chỉ số thuận lợi.

Cuối cùng, chi phí trong lab và ước tính theo kịch bản chưa chứng minh hiệu quả kinh tế thực tế. Phương pháp hiện chưa có bằng chứng để khẳng định tính mới, ưu thế so với quy trình lựa chọn hiện hành hoặc hiệu quả khi áp dụng tại Viettel. Những nhận định đó cần nghiên cứu đối chiếu, ca áp dụng và dữ liệu riêng ngoài phạm vi thiết kế của chương này.

## Tài liệu tham khảo

[1] Bjarnason, E., Åberg, P., và Ali, N. B. (2023). *Software selection in large-scale software engineering: A model and criteria based on interactive rapid reviews*. Empirical Software Engineering. [DOI: 10.1007/s10664-023-10288-w](https://doi.org/10.1007/s10664-023-10288-w).

[2] Farshidi, S., Jansen, S., de Jong, R., và Brinkkemper, S. (2018). *A decision support system for software technology selection*. Journal of Decision Systems. [DOI: 10.1080/12460125.2018.1464821](https://doi.org/10.1080/12460125.2018.1464821).

[3] Kazman, R., Klein, M., và Clements, P. (2000). *ATAM: Method for Architecture Evaluation*. Technical Report CMU/SEI-2000-TR-004, Software Engineering Institute, Carnegie Mellon University. [Bản báo cáo](https://sei.cmu.edu/documents/629/2000_005_001_13706.pdf).

[4] Roy, B., và Słowiński, R. (2013). *Questions guiding the choice of a multicriteria decision aiding method*. EURO Journal on Decision Processes. [DOI: 10.1007/s40070-013-0004-7](https://doi.org/10.1007/s40070-013-0004-7).

[5] Cooper, B. F., Silberstein, A., Tam, E., Ramakrishnan, R., và Sears, R. (2010). *Benchmarking cloud serving systems with YCSB*. Proceedings of the 1st ACM Symposium on Cloud Computing, tr. 143–154. [DOI: 10.1145/1807128.1807152](https://doi.org/10.1145/1807128.1807152).

[6] Kingsbury, K., và Alvaro, P. (2021). *Elle: Inferring Isolation Anomalies from Experimental Observations*. Proceedings of the VLDB Endowment, 14(3), tr. 268–280. [DOI: 10.14778/3430915.3430918](https://doi.org/10.14778/3430915.3430918).

[7] Kalibera, T., và Jones, R. (2013). *Rigorous Benchmarking in Reasonable Time*. Proceedings of the International Symposium on Memory Management, tr. 63–74. [DOI: 10.1145/2464157.2464160](https://doi.org/10.1145/2464157.2464160).

[8] Hoefler, T., và Belli, R. (2015). *Scientific Benchmarking of Parallel Computing Systems: Twelve ways to tell the masses when reporting performance results*. Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis, Article 73. [DOI: 10.1145/2807591.2807644](https://doi.org/10.1145/2807591.2807644).
