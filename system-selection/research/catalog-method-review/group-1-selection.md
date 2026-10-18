# Nhóm 1 — Lựa chọn phần mềm, công nghệ và kiến trúc theo yêu cầu

Ngày khảo sát: 12/10/2026. Đây là ghi chú tổng quan có cấu trúc, không phải chương báo cáo hay systematic literature review đầy đủ. Nguồn chính là toàn văn nhà xuất bản, SEI và bản tác giả. “Đọc toàn văn có chọn lọc” nghĩa là đã đọc các phần được liệt kê, không đồng nghĩa đọc hết bài. Không có bằng chứng hiện trạng hoặc yêu cầu cụ thể của Viettel trong nhóm này.

## Bảng nguồn và phạm vi đọc

| Mã | Nguồn, tác giả, năm | DOI / URL trực tiếp | Loại và phần thực sự đã đọc |
|---|---|---|---|
| S1 | *Software selection in large-scale software engineering: A model and criteria based on interactive rapid reviews* — Elizabeth Bjarnason, Patrik Åberg, Nauman bin Ali (2023), Empirical Software Engineering 28, 51 | [DOI 10.1007/s10664-023-10288-w](https://doi.org/10.1007/s10664-023-10288-w); [toàn văn publisher](https://link.springer.com/article/10.1007/s10664-023-10288-w) | Nghiên cứu gốc thiết kế mô hình dựa trên rapid reviews và practitioner insights. Đọc abstract; phần research design và validation trong §3; §4.1; đoạn requirements §4.2.1; đoạn assess/prototype và integration §4.3; screening/cost §4.4; impact §4.5; §5.1–5.3; §6.2–6.5; §7. Chưa đọc hết mọi tiêu chí §4. |
| S2 | *ATAM: Method for Architecture Evaluation* — Rick Kazman, Mark H. Klein, Paul C. Clements (2000), CMU/SEI-2000-TR-004 | [SEI record](https://insights.sei.cmu.edu/library/atam-method-for-architecture-evaluation/); [toàn văn PDF SEI](https://sei.cmu.edu/documents/629/2000_005_001_13706.pdf) | Báo cáo phương pháp gốc, có ví dụ ứng dụng. Đọc §1.1 (trang in 2–3); đoạn stimulus/response §2 (5); §5.2–5.3 (16–18, đoạn đã mở); §7.1–7.3 (21–23), đầu §7.4 (24); đoạn agenda và mở đầu ca BCS §9.4–10 (42–45); §11 (59–61) và §12 (63). Chưa đọc đầy đủ diễn tiến §10 hay Appendix A. |
| S3 | *A decision support system for software technology selection* — Siamak Farshidi, Slinger Jansen, Rolf de Jong, Sjaak Brinkkemper (2018), Journal of Decision Systems 27(sup1), 98–110 | [DOI 10.1080/12460125.2018.1464821](https://doi.org/10.1080/12460125.2018.1464821); [bản toàn văn tác giả](https://siamakfarshidi.nl/publications/DBMS.pdf); [record Utrecht](https://research-portal.uu.nl/en/publications/a-decision-support-system-for-software-technology-selection) | Nghiên cứu gốc DSS cho DBMS. Đọc abstract; §2; §4 (decision model, case definition, inference engine); §5.1–5.3, riêng phần feature-values §5.2 đọc có chọn lọc; §6 và §7; đoạn đầu §8. Chưa kiểm chứng implementation/link dataset hay đọc toàn bộ bibliography. |
| S4 | *Evaluating and selecting software packages: A review* — Anil S. Jadhav, Rajendra M. Sonar (2009), Information and Software Technology 51(3), 555–563 | [DOI 10.1016/j.infsof.2008.09.003](https://doi.org/10.1016/j.infsof.2008.09.003); [record IIT Bombay](https://dspace.library.iitb.ac.in/xmlui/handle/10054/6585) | Nguồn thứ cấp. Chỉ đọc abstract trong record, không dùng để kết luận phương pháp nào tốt hơn. |

## Ghi chú nguồn chính

### S1

**Tác giả:** Lựa chọn component phải xét môi trường kỹ thuật, kinh doanh và tổ chức. Quy trình lặp: xác định yêu cầu/phương án → đánh giá bằng tài liệu và prototype → sàng lọc tính khả thi → phân tích tác động. Kiểm chứng bằng focus group bốn người tại Ericsson và một ca mở rộng công cụ. **Hạn chế tác giả:** chưa xác nhận khả năng khái quát sang công ty khác và tính đầy đủ tiêu chí; nguy cơ thiên lệch khi phản hồi. **Suy luận áp dụng:** dùng làm khung quy trình và hồ sơ bằng chứng; bổ sung vận hành, chi phí tích hợp/bảo trì, migration. Không sao chép toàn bộ checklist, và không coi tương đồng viễn thông là bằng chứng phù hợp với Viettel. Nghiên cứu hỗ trợ tính hữu ích của quy trình; chưa chứng minh lựa chọn cho catalog tốt hơn về kinh tế.

### S2

**Tác giả:** ATAM đánh giá hậu quả quyết định kiến trúc theo yêu cầu chất lượng; dùng scenario và utility tree để xác định rủi ro, điểm nhạy và đánh đổi. Ca BCS minh họa việc phát hiện yêu cầu thiếu và tương tác performance/availability. **Hạn chế tác giả:** đầu ra phụ thuộc độ chi tiết kiến trúc và sự tham gia stakeholder; không nhằm dự đoán chính xác hiệu năng. Một số chi tiết BCS được đổi để bảo mật/sư phạm. **Suy luận áp dụng:** biến “catalog phải mở rộng tốt” thành scenario có tải và response measure; xác định chỗ cần benchmark. Đây là đánh giá kiến trúc hệ thống, nên dùng phần scenario/risk khi so sánh các cấu hình catalog. Không coi đây là thuật toán xếp hạng sản phẩm hoặc lấy utility tree làm công thức điểm tổng.

### S3

**Tác giả:** DSS hỗ trợ chọn DBMS bằng mô hình tri thức, MoSCoW cho điều kiện cứng/mềm và Weighted Sum cho phương án khả thi. Kiểm chứng: phỏng vấn 14 chuyên gia; ba quyết định tại hai công ty. Kết quả tạo shortlist, cần performance test và TCO thực tế; tác giả khuyến nghị kết hợp benchmark. **Hạn chế tác giả:** yêu cầu/priorities có thể bị cognitive bias; tri thức cần cập nhật. **Suy luận áp dụng:** học cách tách feasibility khỏi preference và quản lý ma trận tính năng có phiên bản. Chưa chấp nhận WSM/MoSCoW mặc định: phải kiểm tra dữ liệu và thang giá trị. DBMS chịu trách nhiệm dữ liệu/truy vấn khác catalog; không chuyển 307 tiêu chí hay workload DBMS. Validation dựa nhiều vào ý kiến và lựa chọn sẵn có; chưa chứng minh tối ưu qua kết quả vận hành dài hạn.

### S4 — chỉ abstract

Abstract báo cáo review theo bốn trục: quy trình lựa chọn, kỹ thuật đánh giá, tiêu chí và công cụ hỗ trợ. Việc AHP được sử dụng rộng không chứng minh AHP phù hợp nhất. Chưa dùng findings như bằng chứng so sánh hiệu quả vì chưa đọc protocol/results.

## Suy luận tổng hợp và giới hạn chuyển miền

Các suy luận dưới đây là đề xuất của người tổng quan, không phải kết luận đã được các tác giả kiểm chứng cho catalog:

- Có căn cứ xem quy trình lựa chọn là lớp riêng với thuật toán tổng hợp. Một quy trình có thể dùng scenario và hồ sơ bằng chứng, rồi mới cân nhắc kỹ thuật tổng hợp nếu cần.
- Với catalog, đơn vị đánh giá nên là phương án triển khai có phiên bản/giao diện/backend/client cụ thể. Đây là chuyển miền đề xuất; ba nguồn chưa kiểm chứng trực tiếp cho sáu catalog của đề tài.
- Ràng buộc tính đúng đắn, phân quyền và tương thích cần có cách chứng minh trước khi đánh đổi hiệu năng/chi phí. S3 là precedent cho tách feasibility/preference, không đủ để chọn sẵn công thức WSM.
- Scenario giúp chọn benchmark theo một bất định liên quan quyết định, thay vì đo tất cả thao tác rồi xếp hạng theo tốc độ.
- Đánh giá phương pháp cần tách: stakeholder thấy hữu ích, kết quả giống lựa chọn trước đó, và lợi ích vận hành/kinh tế được đo. Những loại bằng chứng này có sức mạnh khác nhau.
- Tương đồng viễn thông của Ericsson chỉ là lý do đọc S1; chưa là bằng chứng áp dụng tại Viettel.
- Không chuyển 307 features DBMS, chi phí/reference configuration hay kết quả các DBMS năm 2018 sang catalog.
- Nhận xét về chi phí so sánh cặp/AHP trong related work của S3 là quan điểm tác giả cho nhiều features; chưa đủ để loại AHP trong bài toán sáu catalog.
- Chưa tìm hoặc đọc nghiên cứu lựa chọn trực tiếp technical catalog trong pass này. Không suy ra tính mới từ việc đó.

## Nhật ký tìm kiếm và chọn/loại

| Thứ tự | Truy vấn / thao tác | Kết quả giữ hoặc loại |
|---|---|---|
| 1 | `"Software selection in large-scale software engineering" 2023 full text` | Giữ S1 từ publisher open access; bỏ OpenAlex/J-GLOBAL khỏi bằng chứng nội dung vì chỉ là chỉ mục. |
| 2 | `"ATAM: Method for Architecture Evaluation" 2000 report pdf` | Giữ S2 record và PDF chính thức SEI. Không dùng Wikipedia, Scribd, ResearchGate để phân tích nội dung. |
| 3 | Mở fulltext S1 và S2; tìm headings rồi đọc sections được ghi trên | Có phương pháp, application/validation và hạn chế nên đủ điều kiện nguồn chính. |
| 4 | `Farshidi Jansen de Jong Brinkkemper "database" "decision support" selection full text` | Giữ S3: metadata institutional Utrecht + toàn văn author website; bài gốc và miền gần catalog hơn software package tổng quát. |
| 5 | `"software selection" "2019" "Alégroth" full text` | Tìm thấy *Characteristics that affect preference of decision models for asset selection: an industrial questionnaire survey*, publisher DOI 10.1007/s11219-019-09489-8. Chưa mở fulltext; không đưa vào kết luận. Tạm hoãn vì ba nguồn chính đã phủ quy trình, scenario và case database. |
| 6 | `"Evaluating and selecting software packages: A review" Jadhav Sonar pdf` | Giữ S4 abstract-only để xác định loại nguồn và hướng đọc. Có bản PDF university-hosted trong kết quả nhưng chưa đọc. Không dùng ScienceDirect Topics như bài gốc. |
| 7 | Mở S3 §2, §4–7, đoạn §8; đọc S1 validity, S2 BCS results/conclusions | Đủ evidence để đối chiếu vai trò quy trình, điều kiện bắt buộc, prototype/benchmark và giới hạn validation; dừng pass nhóm 1. |

## Chỗ còn thiếu nếu cần phát triển tiếp

- Kiểm chứng dài hạn hoặc nhiều tổ chức cho quy trình chọn catalog; ba nguồn trên không cung cấp.
- Fulltext và validation độc lập cho một DSS trực tiếp technical catalog; chưa có trong pass này.
- Dữ liệu dự án, stakeholder và ngưỡng chấp nhận để chuyển các scenario/minimum conditions thành bài thử.
- Nhóm MCDA phải tiếp tục xác minh giả định của thang giá trị, compensation, sensitivity và uncertainty; nhóm 1 không chọn AHP/TOPSIS/WSM.

## Kiểm tra hoàn thành nhóm 1

Đã có ba nguồn gốc với toàn văn đọc có chọn lọc; mỗi nguồn có metadata, phạm vi đọc, phương pháp, validation, hạn chế và ứng dụng/giới hạn chuyển sang catalog. Có một review được ghi abstract-only. Chưa viết chương báo cáo, chưa khẳng định phương pháp thắng và chưa khẳng định tính mới.

