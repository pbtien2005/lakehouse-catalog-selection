# Phiếu nguồn: xây cơ sở tri thức cho lựa chọn catalog

Ngày đối chiếu: **15/10/2026**. Chỉ ghi phần thực sự đọc; không mặc định đã đọc toàn bộ vì truy cập được toàn văn. Tất cả ứng dụng sang catalog là đề xuất chuyển miền, chưa có validation trực tiếp.

## Nguồn học thuật và phương pháp

### K01 — Constraint-based Recommender Systems: Technologies and Research Issues

Alexander Felfernig, Robin Burke, 2008, ICEC. [DOI 10.1145/1409540.1409544](https://doi.org/10.1145/1409540.1409544); [metadata TU Graz](https://tugraz.elsevierpure.com/en/publications/constraint-based-recommender-systems-technologies-and-research-is/); [bản do tác giả đăng](https://www.researchgate.net/publication/221550593_Constraint-based_recommender_systems_technologies_and_research_issues).

- Đọc §§1–5 qua bản ghi rõ Alexander Felfernig tải lên; publisher không truy cập được.
- Phân biệt biến nhu cầu, thuộc tính sản phẩm, dữ liệu và ràng buộc; có quan hệ giữa nhu cầu và khả năng đáp ứng.
- Bài phương pháp dẫn các ứng dụng khác, không phải thực nghiệm chọn catalog.
- Áp dụng: tách form, facts và mapping; không suy hiệu quả từ riêng sơ đồ.

### K02 — A decision support system for software technology selection

Siamak Farshidi, Slinger Jansen, Rolf de Jong, Sjaak Brinkkemper, 2018. Journal of Decision Systems 27(sup1), 98–110. [DOI 10.1080/12460125.2018.1464821](https://doi.org/10.1080/12460125.2018.1464821); [PDF tác giả](https://slingerjansen.nl/wp-content/uploads/2018/05/a-decision-support-system-for-software-technology-selection.pdf).

- Đọc §§2,4–7, đối chiếu ghi chú nghiên cứu trước trong workspace.
- DSS dùng mô hình đặc tính, yêu cầu, sàng lọc và weighted sum.
- Đánh giá: 14 chuyên gia, ba quyết định tại hai công ty; còn cần benchmark và TCO thực tế.
- Áp dụng: cấu trúc tri thức và sàng lọc. Không sao chép tiêu chí DBMS hoặc mặc định công thức điểm phù hợp catalog.

### K03 — Ontology Development 101: A Guide to Creating Your First Ontology

Natalya F. Noy, Deborah L. McGuinness, 2001. Stanford technical report KSL-01-05. [HTML tác giả](https://protege.stanford.edu/publications/ontology_development/ontology101-noy-mcguinness.html); [record Stanford](https://protegewiki.stanford.edu/wiki/Ontology101).

- Đọc §§1–3, phần phạm vi, competency questions và kiểu thuộc tính.
- Hướng dẫn thiết kế từ mục đích/câu hỏi tới khái niệm và thuộc tính, phát triển lặp.
- Không phải thử nghiệm so sánh phương pháp; ví dụ chính là wine ontology.
- Áp dụng: viết CQ trước schema. Không coi ontology là thuật toán tự chọn catalog.

### K04 — METHONTOLOGY: From Ontological Art Towards Ontological Engineering

Mariano Fernández, Asunción Gómez-Pérez, Natalia Juristo, **1997**, AAAI Spring Symposium, SS-97-06, pp.33–40. [PDF AAAI](https://cdn.aaai.org/Symposia/Spring/1997/SS-97-06/SS97-06-005.pdf).

- Đọc §§2–4.3,4.5–4.7 và kết luận.
- Tổ chức specification, acquisition, conceptualization, implementation, evaluation, documentation, maintenance; có prototype tiến hóa.
- Hình thành từ kinh nghiệm ontology hóa học, không chứng minh ưu thế cho catalog.
- Áp dụng: thiết kế quy trình biên soạn và đánh giá. Không nhầm ngày đăng lại trang AAAI năm 2023 với năm bài gốc.

### K05 — Knowledge Graphs

Aidan Hogan và cộng sự, 2021, ACM Computing Surveys 54(4), article 71. [DOI 10.1145/3447772](https://doi.org/10.1145/3447772); [bản tác giả trên arXiv](https://arxiv.org/html/2003.02320).

- Đọc chọn lọc §§3.1,3.3,6.5,7.1–7.2; không đọc toàn survey.
- Bàn về schema, ngữ cảnh, open/closed-world assumptions và chất lượng dữ liệu.
- Là survey, không phải phép thử graph database với relational database cho đề tài này.
- Áp dụng: giữ phạm vi và trạng thái chưa biết; dùng CQ và chất lượng theo mục đích để đánh giá.

### K06 — Empirical Evaluation of AI-Assisted Software Package Selection: A Knowledge Graph Approach

Siamak Farshidi, Amir Saberhabibi, Behbod Eskafi, Niloofar Nikfarjam, Sadegh Eskandari, Slinger Jansen, Michel Chaudron, Bedir Tekinerdogan, 2025. **Preprint arXiv v1, 06/08/2025**. [DOI 10.48550/arXiv.2508.05693](https://doi.org/10.48550/arXiv.2508.05693); [toàn văn v1](https://arxiv.org/html/2508.05693v1).

- Đọc chọn lọc §§3–5, nhất là Table 4 và §5.3; chưa chạy artifacts.
- PySelect kết hợp pipeline dữ liệu, KG và diễn giải yêu cầu.
- User study 22 người; Table 4 không cho thấy PySelect cao nhất mọi chỉ số; kiểm định weighted coverage không khác biệt có ý nghĩa.
- Giới hạn: Python/GitHub, tuyển người quen nhóm nghiên cứu, nhãn tham chiếu dùng cả người và LLM.
- Áp dụng kiến trúc; không suy KG tốt hơn mọi LLM hoặc tốt hơn A cho sáu catalog.

### K07 — Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

Patrick Lewis và cộng sự, NeurIPS 2020. [Proceedings](https://papers.nips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html); [toàn văn arXiv v4](https://arxiv.org/html/2005.11401).

- Đọc §§2–3,4.2–4.5; không tái chạy thí nghiệm.
- Kết hợp retrieval và generation, đánh giá QA/generation/fact verification.
- Kết quả NLP không bảo đảm thỏa ràng buộc lựa chọn công nghệ.
- Áp dụng: một lựa chọn cho hỏi đáp tài liệu nếu phát sinh nhu cầu; chưa phải thành phần cần thiết khi dùng form.

### K08 — Structured Prompt Interrogation and Recursive Extraction of Semantics (SPIRES)

J. Harry Caufield và cộng sự, 2024, Bioinformatics 40(3), btae104. [DOI 10.1093/bioinformatics/btae104](https://doi.org/10.1093/bioinformatics/btae104); [publisher](https://academic.oup.com/bioinformatics/article/40/3/btae104/7612230); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10924283/).

- Đọc abstract, phương pháp/algorithm và discussion qua nội dung thân bài được lập chỉ mục. Truy cập trực tiếp publisher lỗi, PMC có captcha; không ghi là đọc trọn toàn văn.
- Trích xuất theo schema và grounding; tác giả yêu cầu kiểm chứng trước khi nhập KB.
- Miền đánh giá chủ yếu khác catalog.
- Ghi nhận hướng acquisition bổ sung; chưa chọn vì người dùng dự kiến LLM chỉ hỗ trợ yêu cầu/giải thích.

## Chuẩn biểu diễn và kiểm tra

### S01 — Decision Model and Notation

[OMG DMN](https://www.omg.org/dmn/). Đã đọc trang giới thiệu mục đích và decision tables; **chưa đọc hết đặc tả, chưa chọn phiên bản hay engine**. Dùng tham khảo biểu diễn quy tắc; chuẩn này không chứng minh tính đúng của khuyến nghị.

### S02 — PROV-O: The PROV Ontology

[W3C Recommendation, 2013](https://www.w3.org/TR/prov-o/). Đọc §2 và phần đầu §3.1 về Entity, Activity, Agent, derivation và responsibility. Tham khảo truy vết nguồn và quá trình duyệt; có thể ánh xạ ý tưởng sang dữ liệu quan hệ mà chưa tuyên bố tuân thủ PROV-O.

### S03 — Shapes Constraint Language

[W3C SHACL](https://www.w3.org/TR/shacl/). Đọc Abstract, §1 và phần tổng quan shapes/constraints có chọn lọc; chưa triển khai validator. Áp dụng nếu chọn RDF. Kiểm tra đồ thị theo điều kiện không xác nhận sự thật của mệnh đề kỹ thuật.

## Cách tìm và chọn nguồn

Các nhóm truy vấn đã dùng gồm:

- `software technology selection knowledge decision support system`;
- `constraint-based recommender systems Felfernig Burke` (nhánh nghiên cứu song song);
- `Ontology Development 101 competency questions Stanford`;
- `METHONTOLOGY From Ontological Art Towards Ontological Engineering`;
- `Knowledge Graphs Hogan schema context quality`;
- `Empirical Evaluation of AI-Assisted Software Package Selection`;
- `Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks`;
- `Structured Prompt Interrogation knowledge bases SPIRES`;
- `catalog selection knowledge-based lakehouse`.

Giữ nguồn gốc: publisher/proceedings, website tác giả, repository trường hoặc bản tác giả trên arXiv; K01 sử dụng bản tải lên có nhận diện tác giả vì publisher không truy cập được. Loại trang tiếp thị và bản tóm tắt tự động khỏi bằng chứng phương pháp. Exa/Firecrawl không có công cụ khả dụng trong phiên; dùng công cụ web sẵn có. Một nhánh được giao subagent kiểm tra K01/K02/K06; báo cáo là tổng hợp nội bộ, không phải phản biện độc lập.

Truy vấn sát lakehouse chưa tìm được nguồn đủ điều kiện để dùng làm bằng chứng thực nghiệm trực tiếp cho hệ chọn sáu catalog. **Điều này không chứng minh không có nghiên cứu hoặc chứng minh tính mới.**

Không tiến hành tìm kiếm có protocol đăng ký trước, không bao phủ mọi cơ sở dữ liệu học thuật, không đọc hết các nguồn liên quan; chưa đủ gọi là SLR hoặc meta-analysis. Nếu đồ án đòi tổng quan hệ thống, cần bổ sung tiêu chí bao gồm/loại trừ, cơ sở dữ liệu, khoảng thời gian, snowballing, nhật ký sàng lọc và đánh giá chất lượng.
