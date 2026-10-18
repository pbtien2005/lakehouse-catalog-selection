# Nhóm 2 — MCDA, ràng buộc, đánh đổi và độ nhạy

Ngày tra cứu: 12/10/2026. Đây là ghi chú tổng quan có cấu trúc, chưa phải chương báo cáo. Chưa chọn thuật toán MCDA cho catalog.

## Nguồn đã xác minh và mức đọc

| ID | Nguồn | DOI/URL | Mức đọc thực tế |
|---|---|---|---|
| M1 | Bernard Roy; Roman Słowiński (2013). Questions guiding the choice of a multicriteria decision aiding method. EURO Journal on Decision Processes 1, 69–97. | [DOI 10.1007/s40070-013-0004-7](https://doi.org/10.1007/s40070-013-0004-7); [full text Springer](https://link.springer.com/article/10.1007/s40070-013-0004-7) | Abstract; Introduction; các đoạn về loại đầu ra trong A crucial question; Five other key questions Q1a–Q1e; Secondary questions Q2a–Q2c; Conclusions. Đọc toàn văn HTML các đoạn này. Lướt các ví dụ bối cảnh, không đọc mọi nghiên cứu được dẫn. |
| M2 | Marco Cinelli; Miłosz Kadziński; Michael Gonzalez; Roman Słowiński (2020). How to support the application of multiple criteria decision analysis? Let us start with a comprehensive taxonomy. Omega 96, 102261. | [DOI 10.1016/j.omega.2020.102261](https://doi.org/10.1016/j.omega.2020.102261); [author manuscript PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7970504/) | Đọc các đoạn thân bài được trả từ bản lập chỉ mục của publisher/PMC: §2 methodology; §3 tổng quan taxonomy; c.3.1.3 thresholds; §3.4.3 rank reversal; §3.5 exploitation; §5 questions/Table 2–3; các đoạn §6 về validation, robustness. Mở trực tiếp PMC bị recaptcha, publisher có lỗi; không tuyên bố đã đọc trọn bài, figures hoặc supplements. Đây không chỉ abstract. |
| M3 | J. Dodgson; M. Spackman; A. Pearman; L. D. Phillips (2009). Multi-criteria analysis: a manual. Department for Communities and Local Government, London. | [PDF chính thức](https://assets.publishing.service.gov.uk/media/5a790545e5274a2acd18b975/1132618.pdf); [LSE repository](https://eprints.lse.ac.uk/12761/1/Multi-criteria_Analysis.pdf) | Đọc chọn lọc §6.2.8–6.2.14, trang in 62–69 (PDF pages 63–70), và Appendix 5–6: đặc biệt 5.2 concerns, 6.1–6.5 outranking/ELECTRE I, trang in 128–138. Không đọc toàn manual 168 PDF pages. Đây là hướng dẫn chính thức, không phải nghiên cứu thực nghiệm gốc. |
| M4 | Thomas L. Saaty (2008). Decision making with the analytic hierarchy process. International Journal of Services Sciences 1(1), 83–98. | [DOI/publisher](https://doi.org/10.1504/IJSSCI.2008.017590); [bản PDF bài gốc](https://www.rafikulislam.com/uploads/resourses/197245512559a37aadea6d.pdf) | Xác minh metadata ở publisher; đọc PDF §1–3 (pp.83–86), Table 1–2, đầu §4 Validation (p.87): cấu trúc so sánh cặp và ví dụ lượng đồ uống. Không tuyên bố đọc trọn bài hoặc kiểm chứng toàn bộ AHP. |

## Phiếu nguồn (kết luận tác giả và chuyển dụng tách riêng)

### M1 — Roy & Słowiński 2013

**Tác giả:** Bài toán là chọn phương pháp MCDA phù hợp bối cảnh. Hệ câu hỏi xét đầu ra, thang đo, thu thập sở thích, bất định, bù trừ, tương tác và khả năng giải thích. Minh họa bằng 12 bối cảnh; không phải thí nghiệm đối chứng. Hướng dẫn không tạo điều kiện đủ để chọn một thuật toán duy nhất; tác giả phản đối chọn phương pháp chủ yếu bằng so sánh ranking mà chúng tạo ra.

**Chuyển dụng của tôi:** Lập phiếu bối cảnh catalog trước khi chọn thuật toán; yêu cầu mentor xác nhận mức bù trừ và loại đầu ra. Bài không xác nhận phương pháp nào hiệu quả riêng cho catalog.

### M2 — Cinelli và cộng sự 2020

**Tác giả:** Taxonomy có ba giai đoạn và mười đặc trưng, tổng hợp 56 công trình từ 948 kết quả tìm kiếm đến tháng 1/2020. Phương pháp là review, phân loại và bộ câu hỏi ánh xạ bài toán–phương pháp; có minh họa ánh xạ đơn giản. Phân biệt sensitivity sau kết luận với robustness trên tập đầu vào khả dĩ. Không chứng minh một phương pháp luôn cho quyết định đúng; các bảng minh họa không phải validation catalog.

**Chuyển dụng của tôi:** Dùng taxonomy làm checklist chọn phương pháp. Ngưỡng veto so sánh hai phương án không thay thế điều kiện đủ tư cách tuyệt đối của hệ thống.

### M3 — MCA manual 2009

**Tác giả:** Hướng dẫn quy trình giá trị cộng, swing weighting, kiểm tra mutual preference independence và sensitivity; có ví dụ tính toán và case studies. Cho phép loại phương án dưới mức chấp nhận. Appendix 6 minh họa ELECTRE I bằng concordance/discordance và shortlist; ví dụ không rút xuống một đáp án duy nhất. Hướng dẫn thiên về quyết định công ở Anh, không phải so sánh thực nghiệm catalog.

**Chuyển dụng của tôi:** Tách eligibility khỏi tổng hợp giá trị; kiểm tra thang đo và đánh đổi trước khi cộng điểm. Quan điểm ưu tiên mô hình cộng của manual không đủ để mặc định nó phù hợp đề tài.

### M4 — Saaty 2008

**Tác giả:** AHP xây hierarchy, so sánh cặp, suy ra ưu tiên rồi tổng hợp theo cấp. Ví dụ dùng đánh giá đồng thuận của khoảng 30 người, đối chiếu tỷ lệ tiêu thụ đồ uống với số liệu thống kê; bảng ghi consistency ratio 0,022. Đây là minh họa phép đo, không phải thử nghiệm chọn công nghệ.

**Hạn chế do tôi đánh giá:** Minh họa trên đại lượng có số liệu đối chiếu không xác nhận “catalog tốt nhất” là chân lý khách quan. Consistency ratio không chứng minh đầu vào có bằng chứng hoặc bao phủ đủ yêu cầu. AHP chỉ là ứng viên nếu có nguồn sở thích và công sức so sánh cặp phù hợp.

## Bản đồ câu hỏi để root dùng khi tổng hợp

Dẫn vị trí chính xác M1, không chọn thuật toán bằng một điểm số meta-MCDA:

- Câu hỏi đầu tiên: loại kết quả cần cung cấp. Có thể là score, ranking, subset/choice, sorting hoặc non-dominated subset.
- Q1a: thang đo ban đầu có phù hợp toán học; mã hóa ordinal thành 1–5 không tự tạo khoảng cách bằng nhau.
- Q1b: có thu được preference information cần thiết qua tương tác không; cần xét arbitrariness và sensitivity.
- Q1c: sai số, bất định và thông tin chưa đầy đủ; không mặc định mọi thiếu hiểu biết có phân phối Gaussian/fuzzy triangular.
- Q1d: có chấp nhận kết quả tốt ở một tiêu chí bù cho kết quả xấu ở tiêu chí khác không.
- Q1e: có tương tác tiêu chí phải mô hình hóa không.
- Q2a: stakeholder hiểu được liên kết đầu vào–khuyến nghị tới mức nào.
- Q2b: các giả định/axioms có được chấp nhận như working hypotheses không.
- Q2c: điểm yếu như rank reversal ảnh hưởng bối cảnh không.
- Conclusions: các câu hỏi chỉ là guidelines, có thể thiếu trong tình huống cụ thể; không có thuật toán tối ưu phổ quát.

## Ba phương án đáng cân nhắc (suy luận thiết kế của tôi)

| Phương án | Đầu vào và cách dùng cho catalog | Khi đáng thử | Hạn chế và điều kiện trước khi dùng |
|---|---|---|---|
| A. Ràng buộc → Pareto → phân tích kịch bản/đánh đổi | Xác định yêu cầu bắt buộc; giữ “chưa xác minh” riêng; xét trội trên các chiều so sánh được; diễn giải trade-off bằng bằng chứng và scenario. | Sở thích chưa đủ rõ hoặc dữ liệu chủ yếu định tính; mục tiêu shortlist. | Pareto có thể giữ nhiều phương án; không tự chọn ra một catalog; thiếu dữ liệu không cho phép chứng minh trội. Kịch bản cần phép kiểm tra cụ thể. |
| B. Ràng buộc → mô hình giá trị cộng → sensitivity | Chỉ tổng hợp các phương án đủ điều kiện; chuyển performance thành giá trị có ý nghĩa; lấy trọng số gắn với khoảng cải thiện (swing). | Có đầu vào định lượng/giá trị hợp lệ và người xác nhận các đánh đổi; muốn giải thích đóng góp từng tiêu chí. | Cần xét preference independence, bù trừ, trùng tiêu chí, thang điểm và range. AHP có thể được khảo sát cho elicitation; không đồng nhất AHP với toàn bộ pipeline. |
| C. Ràng buộc → outranking → sensitivity/robustness | Sau screening, so sánh theo concordance và phản bác/veto; cho phép shortlist hoặc quan hệ chưa so sánh được. | Một số đánh đổi không được chấp nhận; chỉ khác biệt vượt ngưỡng mới có ý nghĩa. | Cần xác nhận weights/thresholds và giải thích quan hệ. Chưa chọn ELECTRE I/III/TRI hay PROMETHEE. Nếu đi tiếp cần đọc nguồn nguyên thủy của variant và tự kiểm tra tính toán; mức đọc hiện đủ so sánh họ phương pháp, chưa đủ làm đặc tả triển khai một variant. |

Các pipeline trong bảng là đề xuất thích nghi, không phải nguyên văn phương pháp catalog do bốn nguồn trên đã kiểm chứng. Bằng chứng hiện đủ phân biệt ba hướng; chưa đủ chọn hướng thắng khi chưa có yêu cầu, sở thích và dữ liệu dự án.

TOPSIS đã được nhận diện trong M1 và M2, nhưng chưa đọc nguồn gốc Hwang & Yoon đầy đủ nên không lập một lựa chọn TOPSIS riêng. Có thể đọc thêm nếu quyết định nghiên cứu distance-to-ideal, normalization và rank reversal; không nên thêm chỉ để có nhiều thuật toán.

## Các điểm cần tránh khi chuyển sang catalog (suy luận)

- Eligibility gate kiểm tra “catalog có đáp ứng yêu cầu tối thiểu X không”; veto kiểm tra “A quá kém B ở chiều X nên không được kết luận A ít nhất tốt bằng B”. Hai phép này khác nhau.
- Đơn vị so sánh phải là phương án triển khai đúng phiên bản/đường tích hợp. Một score theo tên sản phẩm không xử lý phụ thuộc engine, format và backend.
- “Không hỗ trợ”, “chưa xác minh”, “không áp dụng” là ba trạng thái khác. Đừng biến thiếu nguồn thành zero hoặc pass.
- Ví dụ tương tác cần xác nhận: giá trị credential vending phụ thuộc đường truy cập engine; federation phụ thuộc connector/backend. Có thể cấu trúc lại criteria hoặc đánh giá cấu hình thay vì thêm toán học phức tạp.
- Độ nhạy cần thay cả performance/chi phí và preference parameters; chỉ đổi weights không phủ hết bất định.
- Dữ liệu benchmark là performance evidence; không trực tiếp tạo preference weights hoặc chứng minh maturity/hiệu quả kinh tế.
- Nếu nhiều đầu vào bất định, kiểm tra một biến mỗi lần có thể chưa đủ. Trước tiên khoanh các biến có thể làm đảo shortlist, tránh Monte Carlo khi không có căn cứ cho phân phối.

## Nhật ký tìm kiếm và truy cập

| Bước | Truy vấn/URL thực tế | Kết quả sử dụng |
|---|---|---|
| 1 | Mở Springer DOI M1, DOI M2 và PDF GOV manual. | M1 và manual đọc được; DOI M2 ban đầu lỗi. |
| 2 | “A taxonomy of multi-criteria decision analysis methods” Cinelli 2020 pdf; “Questions guiding the choice” Roy Slowinski pdf. | Xác nhận tên thật M2 khác cách gọi ngắn; tìm DOI và publisher; bỏ các thesis/blog không cần thiết. |
| 3 | “How to support the application of multiple criteria decision analysis” filetype:pdf; “Cinelli” “102261” pdf repository. | Tìm author manuscript PMC7970504; RePEc chỉ dùng định vị, không thay bài gốc. |
| 4 | Mở PMC, PMC ?pdf=1, ?report=xml, và NCBI BioC URL. | Recaptcha/lỗi; không tuyên bố mở full article thành công. |
| 5 | Tìm “PMC7970504” với “thresholds”, “veto”, “robustness”, “rank reversal”, “3.4.1”. | Web trả các đoạn thân bài của chính PMC và publisher; đọc chọn lọc theo ledger M2. |
| 6 | “Decision making with the analytic hierarchy process” Saaty 2008 pdf. | DOI publisher metadata + PDF bài gốc; đọc §3/Table 1–2 và đầu validation. |
| 7 | “Multi-criteria analysis: a manual” Dodgson Spackman Pearman Phillips 2009, domain eprints.lse.ac.uk. | Metadata tên tác giả được đối chiếu với citation trong tài liệu LSE của Phillips; PDF chính thức là bản đọc chính. LSE có robots restriction. |

## Giới hạn của lượt đọc

Không tiến hành exhaustive/systematic review; không đọc supplements của M2; không đọc original TOPSIS hoặc original ELECTRE III. Không có nguồn nào ở nhóm này benchmark sáu catalog hoặc xác nhận trọng số cho Viettel. Các khó khăn truy cập được giải quyết bằng nguồn chính thức/đoạn thân bài khả dụng, không dùng nội dung abstract để thay cho kết quả của phần chưa đọc.

