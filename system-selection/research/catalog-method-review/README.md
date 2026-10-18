# Tổng quan tài liệu có kiểm chứng: lựa chọn phương pháp đánh giá technical catalog

Ngày đối chiếu: **12/10/2026**. Phạm vi là phương pháp lựa chọn theo yêu cầu, MCDA, benchmark/correctness/reproducibility. Đây là hồ sơ nghiên cứu có cấu trúc, **không phải chương báo cáo cuối**, không phải exhaustive/systematic review, không phải kết quả benchmark sáu catalog.

## Kết quả và mức bằng chứng

Đã ghi nhận **13 nguồn học thuật/phương pháp**: 11 nguồn đọc trực tiếp các phần của toàn văn, 1 nguồn đọc các đoạn thân bài qua bản lập chỉ mục (M2), 1 review chỉ đọc abstract (S4). Có thêm **7 hồ sơ tài liệu chính thức** để xác minh các nhận định công nghệ hẹp. Phạm vi đọc chỉ gồm phần liệt kê trong phiếu nguồn, không có nghĩa đã đọc hết bài hoặc kiểm chứng lại thực nghiệm tác giả.

Bằng chứng đủ để so sánh **ba họ phương pháp ứng dụng** A/B/C bên dưới. Chưa đủ để kết luận phương pháp nào phù hợp nhất với dự án Viettel hoặc chọn một catalog cụ thể. Các pipeline là suy luận thích nghi của người tổng quan, chưa được các nguồn kiểm chứng trực tiếp trên sáu catalog.

## Bảng nguồn

Phiếu chi tiết ghi riêng bài toán, phương pháp, kiểm chứng, hạn chế tác giả và suy luận áp dụng:

- [Nhóm 1: lựa chọn phần mềm/kiến trúc/DBMS](group-1-selection.md).
- [Nhóm 2: MCDA, ràng buộc, đánh đổi, độ nhạy](group-2-mcda.md).
- [Nhóm 3: benchmark, correctness, tái lập](group-3-benchmark.md).
- [Nguồn sát catalog và tài liệu chính thức](official-source-notes.md).

| ID | Tên, tác giả, năm | DOI / URL | Phần thực sự đọc; vai trò trong tổng quan |
|---|---|---|---|
| S1 | *Software selection in large-scale software engineering: A model and criteria based on interactive rapid reviews* — Elizabeth Bjarnason, Patrik Åberg, Nauman bin Ali, 2023 | [10.1007/s10664-023-10288-w](https://doi.org/10.1007/s10664-023-10288-w) | Chọn lọc §§3–7: design/validation, quy trình, prototype, screening, impact, validity. Khung quy trình theo bối cảnh. |
| S2 | *ATAM: Method for Architecture Evaluation* — Rick Kazman, Mark H. Klein, Paul C. Clements, 2000 | [SEI/CMU-SEI-2000-TR-004](https://insights.sei.cmu.edu/library/atam-method-for-architecture-evaluation/) | Chọn lọc §§1–2,5,7,9–12; utility tree, scenario, sensitivity/tradeoffs và ca BCS. Phân tích rủi ro kiến trúc. |
| S3 | *A decision support system for software technology selection* — Siamak Farshidi, Slinger Jansen, Rolf de Jong, Sjaak Brinkkemper, 2018 | [10.1080/12460125.2018.1464821](https://doi.org/10.1080/12460125.2018.1464821) | §§2,4–7 và đầu §8; §5.2 chọn lọc. Case DBMS, điều kiện cứng/mềm và giới hạn shortlist. |
| S4 | *Evaluating and selecting software packages: A review* — Anil S. Jadhav, Rajendra M. Sonar, 2009 | [10.1016/j.infsof.2008.09.003](https://doi.org/10.1016/j.infsof.2008.09.003) | **Chỉ abstract**. Định vị lĩnh vực; không dùng để so sánh hiệu quả phương pháp. |
| S5 | *Reproducible data science over data lakes: replayable data pipelines with Bauplan and Nessie* — Jacopo Tagliabue, Ciro Greco, 2024 | [arXiv DOI 10.48550/arXiv.2404.13682](https://doi.org/10.48550/arXiv.2404.13682) | Preprint v1: §§1–5,7; Table 1, captions/listings. Workflow sát catalog; không phải comparative catalog benchmark. |
| M1 | *Questions guiding the choice of a multicriteria decision aiding method* — Bernard Roy, Roman Słowiński, 2013 | [10.1007/s40070-013-0004-7](https://doi.org/10.1007/s40070-013-0004-7) | Introduction, crucial question, Q1a–Q1e, Q2a–Q2c, Conclusions. Chọn phương pháp theo cấu trúc bài toán. |
| M2 | *How to support the application of multiple criteria decision analysis? Let us start with a comprehensive taxonomy* — Marco Cinelli, Miłosz Kadziński, Michael Gonzalez, Roman Słowiński, 2020 | [10.1016/j.omega.2020.102261](https://doi.org/10.1016/j.omega.2020.102261); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7970504/) | **Đoạn thân bài được lập chỉ mục** §§2–3,5–6; thresholds, rank reversal, exploitation. Truy cập trực tiếp lỗi/recaptcha; chưa đọc trọn article/figures/supplements. |
| M3 | *Multi-criteria analysis: a manual* — J. Dodgson, M. Spackman, A. Pearman, L. D. Phillips, 2009 | [PDF chính thức](https://assets.publishing.service.gov.uk/media/5a790545e5274a2acd18b975/1132618.pdf) | §§6.2.8–6.2.14, Appendices 5–6 chọn lọc. Hướng dẫn chính thức, không phải paper thực nghiệm; mô hình cộng và ELECTRE I. |
| M4 | *Decision making with the analytic hierarchy process* — Thomas L. Saaty, 2008 | [10.1504/IJSSCI.2008.017590](https://doi.org/10.1504/IJSSCI.2008.017590) | §§1–3, Tables 1–2 và đầu §4. AHP là ứng viên, không được chọn sẵn. |
| B1 | *Benchmarking Cloud Serving Systems with YCSB* — Brian F. Cooper, Adam Silberstein, Erwin Tam, Raghu Ramakrishnan, Russell Sears, 2010 | [10.1145/1807128.1807152](https://doi.org/10.1145/1807128.1807152) | PDF trực tiếp §§4–6.1,7.2,9; các phần khác đọc chọn lọc; §6.6–7 qua text index. Chưa đọc kỹ graphs 6.2–6.5. Workload/adapter và latency–throughput. |
| B2 | *Rigorous Benchmarking in Reasonable Time* — Tomas Kalibera, Richard E. Jones, 2013 | [10.1145/2464157.2464160](https://doi.org/10.1145/2464157.2464160); [Kent manuscript](https://kar.kent.ac.uk/33611/45/p63-kaliber.pdf) | PDF 2–4,10–12: §§1,3–4,9.3–12. Phần giữa chỉ thấy chọn lọc, chưa đọc chứng minh technical report. Lặp và bất định. |
| B3 | *Elle: Inferring Isolation Anomalies from Experimental Observations* — Kyle Kingsbury, Peter Alvaro, 2021 theo Reference Format PVLDB; preprint 2020 | [10.14778/3430915.3430918](https://doi.org/10.14778/3430915.3430918) | Chọn lọc §§3.1–3.3; §§4.2,5,6–6.1; rà thêm §2.1 về traceability/history. Không đọc liên tục toàn §3. Correctness checker có điều kiện. |
| B4 | *Scientific Benchmarking of Parallel Computing Systems: Twelve Ways to Tell the Masses when Reporting Performance Results* — Torsten Hoefler, Roberto Belli, 2015 | [10.1145/2807591.2807644](https://doi.org/10.1145/2807591.2807644) | §§2–4,5.2,6 và 12 rules; chưa đọc sâu §5.1. Thiết kế/công bố thí nghiệm. |

Tài liệu chính thức D1–D7 gồm Iceberg REST/OpenAPI, Polaris Benchmarks, HMS REST, Iceberg–Glue optimistic locking, Gravitino IRC, Unity Catalog UniForm và Nessie Specification. Tên/tổ chức/phiên bản/phần đọc/giới hạn có trong bảng riêng tại `official-source-notes.md`.

## Tổng hợp các cách tiếp cận

Các kết luận sau là **suy luận của người tổng quan** từ tập nguồn, không phải kết quả đã được tác giả kiểm chứng cho catalog:

1. **Quy trình lựa chọn và phép tổng hợp kết quả là hai lớp.** Có thể hoàn thiện hồ sơ yêu cầu, scenario, bằng chứng và shortlist trước khi quyết định cần ranking số hay không.
2. **Yêu cầu bắt buộc cần kiểm tra tư cách phương án riêng.** Gate tuyệt đối khác veto tương đối trong một phép so sánh cặp. Nhiều tính năng hoặc tốc độ cao không bù được một yêu cầu bắt buộc bị vi phạm.
3. **Chọn phương pháp bằng khả năng phù hợp với dữ liệu/sở thích.** Cần biết mục tiêu choice/shortlist/ranking, thang đo, mức bù trừ, tương tác và bất định. Không chọn công thức vì nó cho catalog đứng đầu mong muốn.
4. **Các loại validation có sức mạnh khác nhau.** Hữu ích theo mentor, phù hợp lựa chọn trước đây, chạy đúng trong lab và tiết kiệm đo ngoài thực tế là các kết luận khác nhau. Không suy tối ưu từ sự đồng thuận.
5. **Benchmark là bằng chứng có điều kiện.** Workload KV, HPC intervals hoặc database isolation không chuyển nguyên sang catalog. Contract và đường tích hợp quyết định phép đo/oracle cần dùng.

## Ba phương án phương pháp đáng cân nhắc

| Phương án thích nghi | Cách nối tới quyết định | Căn cứ đọc | Khi phù hợp | Đánh đổi và phần chưa đủ |
|---|---|---|---|---|
| **A. Lọc bắt buộc → phân tích kịch bản → Pareto/shortlist và hồ sơ đánh đổi** | Yêu cầu có nguồn → điều kiện/response measure → bằng chứng → khả thi/không khả thi/chưa xác minh → trội trên các chiều đủ dữ liệu → shortlist có lý do | S1/S2 cho quy trình/scenario; S3 cho feasibility; M1 cho đầu ra non-dominated/choice | Sở thích chưa rõ, dữ liệu định tính nhiều, nguồn lực sinh viên; cần giải thích lựa chọn theo ca | Có thể còn nhiều phương án. Chỉ kết luận Pareto khi các chiều liên quan đủ dữ liệu; thiếu dữ liệu hoặc khoảng chồng lấn không chứng minh trội. Không tạo ranking bắt buộc. |
| **B. Lọc bắt buộc → mô hình giá trị cộng → phân tích độ nhạy** | Sau gate, biến evidence thành giá trị được stakeholder chấp nhận; elicitation preference; tổng hợp và kiểm tra kết quả trên đầu vào khả dĩ | M3 cho value model; M1 cho assumptions; S3 cho precedent DBMS; M4 giúp khảo sát elicitation | Có người xác nhận sở thích, dữ liệu/thang giá trị đủ tốt; cần giải thích đóng góp từng yếu tố | Cần kiểm tra bù trừ, preference independence, thang giá trị và trùng lợi ích. Không tự coi ordinal 1–5 là interval. Không lấy benchmark làm weights. AHP có thể là cách lấy sở thích nếu được chứng minh phù hợp, chưa mặc định dùng. |
| **C. Lọc bắt buộc → outranking → shortlist/quan hệ so sánh và độ nhạy** | Sau gate, xem bằng chứng ủng hộ/phản bác quan hệ giữa phương án; kiểm tra thresholds/veto nếu variant hỗ trợ; có thể giữ incomparability | M1/M2 cho lựa chọn họ phương pháp; M3 Appendix6 cho minh họa ELECTRE I | Stakeholder cần hạn chế bù trừ hoặc khác biệt nhỏ không có ý nghĩa; chấp nhận kết quả không phải total ranking | Nhiều tham số và công giải thích hơn. Veto không thay gate. **Chưa đủ để chọn/đặc tả ELECTRE III, TRI hay PROMETHEE**; cần đọc nguồn variant nếu tiến tới triển khai. |

TCO có thể cung cấp một chiều kinh tế hoặc một phép kiểm tra khả thi trong cả ba phương án; chưa có đơn giá, baseline hay kỳ đánh giá của Viettel. TOPSIS được nhận diện qua M1/M2 nhưng chưa đọc nguồn gốc đủ sâu, nên không đưa thành phương án thứ tư hoặc kết luận nó kém hơn. Bằng chứng hiện không buộc chọn AHP, TOPSIS, weighted score hay outranking.

## Vai trò benchmark và chuyển miền

Chuỗi đề xuất: **yêu cầu có nguồn → tiêu chí/phép kiểm tra → phương án triển khai cụ thể → bằng chứng tài liệu/thí nghiệm → xử lý theo A/B/C → khuyến nghị có điều kiện**. Mỗi evidence record giữ nguồn, phiên bản, thao tác, cấu hình, trạng thái và phạm vi kết luận. Tám nhóm kỹ thuật cùng các nhóm vận hành/chi phí/migration/maturity là đầu vào rà soát, không mặc định tất cả được cộng điểm.

Benchmark phục vụ điểm bất định có thể đổi quyết định. Trước thí nghiệm cần ghi khuyến nghị tạm thời và câu hỏi cần đo; sau đó kiểm tra kết quả đo thay đổi feasibility, trade-off hay mức tin cậy nào. Không thay đổi kết luận cũng là kết quả hợp lệ.

| Miền nguồn | Phần chuyển được (suy luận) | Phần phải xây lại cho catalog |
|---|---|---|
| Software/DBMS selection | Quy trình, knowledge/evidence register, screening, thử nghiệm sau shortlist | Ranh giới metadata/data/engine/storage; criteria và phụ thuộc phiên bản; không chuyển307 DBMS features hoặc chi phí/case 2018 |
| ATAM | Scenario/response measure, rủi ro và điểm cần thử | Áp dụng nhẹ cho phương án catalog; không tuyên bố đã thực hiện ATAM đầy đủ hoặc dự đoán hiệu năng từ utility tree |
| YCSB | Tách workload/adapter/measurement, thay đổi tải và phân bố | Load-table/commit/namespace semantics; việc công bố metadata; auth và retry |
| Elle | Lịch sử có ID, invocation/completion, dependency và phản ví dụ | Chứng minh mapping transaction/object/observable-state; không dùng oracle chung cho mọi catalog |
| Statistical/HPC benchmark | Pilot, nguồn biến thiên, lặp, uncertainty, manifest và raw results | Client mạng, service/backend/cache, percentile latency và khác biệt managed/self-hosted |
| Bauplan/Nessie | Trạng thái code/data/runtime cần giữ khi replay | Không suy catalog một mình làm pipeline deterministic hoặc branch là yêu cầu mọi hệ thống |

**Ví dụ oracle giới hạn:** với append-only và ID duy nhất, có thể đối chiếu tập cập nhật đã được xác nhận để tìm mất/lặp. Với overwrite/delete, giá trị cũ biến mất có thể đúng: phải kiểm tra lịch sử theo hợp đồng thao tác. Conflict hợp lệ không mặc định là failure chất lượng; timeout chưa xác định không mặc định là abort. Không thấy phản ví dụ trong hữu hạn lần chạy không chứng minh correctness phổ quát.

Phương án đánh giá là catalog + phiên bản + API + backend + engine/client + format/storage + cấu hình liên quan. D1/D3/D4/D5/D6/D7 cho thấy không thể đồng nhất endpoint, quyền hoặc commit chỉ theo tên sản phẩm. Tài liệu chính thức chưa thay thế runtime test; nguồn main/develop chưa đại diện một release production.

## Khoảng trống và quyết định dừng

- Đủ căn cứ **so sánh ba họ phương pháp**, nhưng chưa chọn một họ cho hồ sơ dự án chưa xác định.
- Chưa có validation độc lập rằng A/B/C cải thiện quyết định chọn technical catalog, hiệu quả kinh tế dài hạn hoặc phạm vi áp dụng Viettel. Cần ca áp dụng và dữ liệu mới; đây không phải thiếu nguồn khiến ba họ không so sánh được.
- Chưa đủ nguồn để triển khai variant outranking cụ thể hoặc đánh giá TOPSIS trực tiếp. Chỉ bổ sung nếu chọn nghiên cứu hướng đó.
- Chưa có yêu cầu/threshold, workload đại diện, tolerance uncertainty, resources hay baseline/đơn giá xác nhận. Không giả định chúng từ lab sẵn có.
- Không kết luận tính mới từ việc tìm kiếm chưa trả về nghiên cứu trực tiếp catalog. Các query logs chỉ mô tả lượt khảo sát này.

**Dừng lượt tổng quan tại đây:** cả ba nhóm đã có nguồn đọc ngoài abstract, cách kiểm chứng/hạn chế được ghi, ba phương án có căn cứ và điều kiện khác nhau. Chưa viết chương cuối, chưa chạy benchmark mới, chưa chọn catalog.

## Audit hoàn thành theo yêu cầu người dùng

| Yêu cầu | Bằng chứng hiện có | Trạng thái |
|---|---|---|
| Tìm và đọc ba nhóm | S1–S3; M1–M4; B1–B4; query logs ở từng nhóm | Đạt cho tổng quan có cấu trúc |
| Ưu tiên nghiên cứu gốc, xác minh công nghệ chính thức | Các nguồn gốc có phương pháp/validation; M2/S4 là review, M3 manual được ghi rõ; D1–D7 official | Đạt |
| Tên/tác giả/năm/DOI hoặc URL | Bảng nguồn và các phiếu | Đạt |
| Mức đọc, abstract-only | S4 abstract; M2 indexed-body; boundaries từng source | Đạt |
| Problem/method/validation/limitations/applicability | Phiếu chi tiết từng nhóm, S5 và D1–D7 | Đạt |
| Bảng nguồn, tổng hợp, 2–3 phương án | README và bảng A/B/C | Đạt |
| Tác giả khác suy luận, giới hạn chuyển miền | Nhãn trong phiếu, synthesis và bảng transfer | Đạt |
| Không bịa nguồn/khẳng định mới, không viết chương cuối | URLs/metadata đối chiếu; explicit limits | Đạt trong phạm vi đã khảo sát |

Rà soát độc lập phát hiện và đã sửa một oracle quá rộng: mọi giá trị từng commit không cần còn trong final state khi overwrite/delete hợp lệ. Tổng quan không dựa vào điều kiện sai đó để đánh giá catalog.
