# Lựa chọn catalog khi giả định KB chính xác và đầy đủ

Ngày nghiên cứu: **17/10/2026**. Đầu vào: file `Pasted text.txt` người dùng cung cấp trong lượt này. Đối chiếu với [input v1](input-v1.md), [lớp tri thức kỹ thuật](layer-1-design.md), [flow trước](decision-flow.md) và [suy luận nâng cao](advanced-reasoning.md).

**Trạng thái:** tổng quan có chọn lọc và đề xuất phương pháp; đã kiểm tra tám ví dụ toán học giả định bằng Python, chưa triển khai hệ khuyến nghị, chưa kiểm nghiệm sáu catalog hoặc khảo sát người dùng. Giả định KB hoàn hảo phục vụ cô lập bài toán quyết định, không mô tả chất lượng KB thực tế hiện có.

## 1. Kết luận nghiên cứu

Có thể lấy **lọc ràng buộc kết hợp + mô hình giá trị cộng + giải thích và độ nhạy** làm thiết kế cơ sở để thử nghiệm. Weighted Sum chỉ là bước tổng hợp sau khi đã xác lập thang giá trị và sở thích; dữ liệu kỹ thuật đầy đủ chưa đủ để tính một mức phù hợp duy nhất.

Cần phân biệt ba lớp:

1. **Sự thật kỹ thuật:** catalog làm được gì trong phạm vi nào. Giả định đã biết đầy đủ.
2. **Yêu cầu của ca lựa chọn:** doanh nghiệp cần gì, điều gì bắt buộc, thao tác nào phải cùng hoạt động. Vẫn có thể chưa rõ.
3. **Mô hình giá trị:** doanh nghiệp đánh giá các đánh đổi ra sao. Không suy ra trực tiếp từ sự thật kỹ thuật.

Minimax regret giải quyết cả trường hợp **sở thích chưa xác định**, nên lý do “KB đầy đủ thì không còn vai trò” trong file đầu vào chưa đúng. Có thể để nó ngoài lõi v1 vì muốn giảm phạm vi, hoặc vì người dùng đã xác nhận đầy đủ mô hình giá trị. [Boutilier et al., 2006, abstract và §3](https://www.cs.toronto.edu/~cebly/Papers/BPPS-aij06.pdf)

Các phần dưới là **đề xuất thích nghi cho miền catalog**, không phải kết luận một nguồn đã thực nghiệm và chứng minh pipeline này tốt nhất.

## 2. Xử lý từng đề xuất trong file đầu vào

| Vấn đề/đề xuất | Kết luận | Cách xử lý cụ thể |
|---|---|---|
| Chuyển form thành Hard/Soft | Giữ, bổ sung **Context** | Hiện trạng không tự thành bắt buộc; mỗi phép ánh xạ phải có quy tắc và nguồn input |
| Bỏ UNKNOWN khi KB hoàn hảo | Đúng có điều kiện | Bộ kiểm tra kỹ thuật có thể trả true/false khi yêu cầu đã rõ, miền xét hữu hạn/được xác định và evaluator quyết định được; input chưa rõ hoặc solver chưa xong vẫn phải báo riêng |
| Lọc các yêu cầu bắt buộc | Giữ | Tìm **một phạm vi nhất quán cùng thỏa mọi yêu cầu**, không AND các ô tính năng độc lập |
| Conflict diagnosis và nới yêu cầu | Giữ | Tách tập xung đột khỏi tập sửa chữa; chỉ mô phỏng sửa các yêu cầu được phép thay đổi |
| Pareto là tầng tùy chọn | Đồng ý | Dùng để giải thích/kiểm tra; không bắt buộc xóa phương án trước ranking; chú ý trường hợp trọng số bằng 0 |
| Weighted Sum làm phương pháp chính | Chọn làm baseline có điều kiện | Dùng giá trị đã hiệu chỉnh, không cộng trực tiếp nhãn thứ bậc hoặc số tính năng |
| Dùng bộ trọng số mặc định | Chỉ là giả định chính sách | Ghi người xây, thang/range, phiên bản; cho xem và xác nhận; chưa xác nhận thì kết quả là theo preset |
| Bỏ minimax vì không còn bất định kỹ thuật | Sửa lý do | Ngoài lõi v1; vẫn có thể cần khi ưu tiên chưa đầy đủ và buộc phải chọn |
| Bỏ Active Information Acquisition | Tách hai việc | Có thể bỏ vòng xác minh kỹ thuật theo giả định; vẫn có thể hỏi để làm rõ yêu cầu và đánh đổi |
| SMAA-lite chỉ là sensitivity | Cần định nghĩa lại | Dùng sensitivity xác định làm mặc định; lấy mẫu trọng số chỉ là phân tích theo phân phối đã khai báo, không tự mang nghĩa xác suất chọn đúng |
| Risk flags tùy chọn | Tách cảnh báo ra khỏi điểm | Vi phạm bắt buộc luôn phải giải thích; các nhãn rủi ro khác chỉ có khi thuộc mục tiêu nghiên cứu và có định nghĩa |
| Bảng A=4,50, B=4,20 | Phép cộng đúng | Chưa chứng minh thang 1–5 là thang giá trị hợp lệ; điểm không phải tỷ lệ đáp ứng mọi yêu cầu |

## 3. Vấn đề 1 — Mô hình hóa yêu cầu và quan hệ phụ thuộc

### 3.1. Hợp đồng giữa form và bộ suy luận

Một yêu cầu được chuẩn hóa nên có:

```text
id; source_answer; kind = HARD | SOFT | CONTEXT;
predicate / objective; AND/OR; scope; operation;
threshold nếu có; relaxable; mapping_revision.
```

Một tiêu chí mềm cần thêm đại lượng đánh giá, đơn vị/thứ bậc, chiều tốt/xấu, hàm giá trị và lý do liên quan tới mục tiêu. `nice-to-have` xác định vai trò ưu tiên, chưa xác định trọng số.

Đối chiếu bộ hỏi đã chốt:

| Input hiện hành | Quy tắc đề xuất cho lớp quyết định |
|---|---|
| I01 nơi chạy, I09 nền tảng gắn bó | Bối cảnh; chỉ thành HARD khi có điều kiện phải giữ/điều khoản bắt buộc |
| I02 engine, I03 format | Kiểm tra tổ hợp được yêu cầu, cùng thao tác/phạm vi; “hỗn hợp” chưa xác định tập format cần dùng |
| I04 số bảng, I05 số engine ghi, I06 streaming nếu giữ | Bối cảnh workload; không tạo ngưỡng loại hoặc ưu tiên tự động chỉ từ nhãn quy mô |
| I07 mức quyền, I08 vending | Sinh yêu cầu đúng điểm thực thi và phạm vi; chưa rõ nhu cầu phải được giữ là thiếu input |
| I10 nhu cầu đặc thù | Bắt buộc → HARD; nice-to-have → SOFT; chưa chọn mức → chưa phân loại được |

**Khoảng trống quyết định:** input v1 chưa hỏi trọng số, thang đánh đổi, storage cụ thể, thao tác của từng engine hoặc mục tiêu công vận hành. Vì vậy, ví dụ “Iceberg + Spark + Trino + MinIO + on-prem” chưa được đặc tả hết bằng form hiện tại. Nghiên cứu này đề xuất hợp đồng xử lý, **không tự bổ sung câu hỏi vào bản input đã chốt**.

Nếu giữ nguyên form, kết quả giới hạn theo thông tin đã có: shortlist, ranking theo preset có nhãn, hoặc ranking theo phần sở thích đã được xác nhận. Không tự thêm mục tiêu “giảm vận hành” cho mọi doanh nghiệp.

### 3.2. Kiểm tra tương thích kết hợp

Gọi `c` là catalog, `q` là một phạm vi/tổ hợp hợp lệ của catalog trong bối cảnh `u`, `H` là tập yêu cầu bắt buộc. Dùng:

\[
F(H,u)=\{(c,q):q\in Q(c,u),\ D(c,q,u)\land\bigwedge_{h\in H}h(c,q,u)\}.
\]

`D` là các quan hệ miền: phiên bản, connector, thao tác, storage và các phụ thuộc liên quan. Catalog đủ điều kiện nếu có ít nhất một cặp `(c,q)` trong F. Phiên bản/edition là phạm vi kiểm chứng, đầu ra người dùng vẫn là công nghệ catalog.

Sai lầm cần ngăn:

\[
\forall h\in H,\ \exists q:h(c,q,u)
\quad\not\Rightarrow\quad
\exists q:\bigwedge_{h\in H}h(c,q,u).
\]

Ví dụ giả định: phạm vi q1 chỉ đáp ứng Spark-write; q2 chỉ đáp ứng Trino-read. Catalog có “Spark” và “Trino” ở hai ô riêng nhưng không có phạm vi cùng đáp ứng hai thao tác. E01 đã kiểm tra phản ví dụ này. Không có kết luận về sản phẩm thật.

Phải kiểm tra các quan hệ nhiều chiều khi chúng ảnh hưởng tính khả thi; hỗ trợ từng cặp cũng chưa bảo đảm tương thích toàn tổ hợp. Cách biểu diễn có thể là bảng tổ hợp, predicate hoặc luật điều kiện. Với sáu công nghệ và miền nhỏ, duyệt phạm vi là baseline dễ thẩm định; SAT/SMT/CSP là lựa chọn triển khai khi không gian lựa chọn lớn hơn, không tự làm mô hình đúng hơn.

Tiền lệ DSS chọn công nghệ đã tách điều kiện bắt buộc khỏi đánh giá các phương án khả thi. Tuy nhiên, nghiên cứu DBMS không xác nhận sẵn bộ tiêu chí hoặc quy tắc tương thích catalog ở đây. [Farshidi et al., 2018, §§4.2–4.3](https://slingerjansen.nl/wp-content/uploads/2018/05/a-decision-support-system-for-software-technology-selection.pdf)

### 3.3. Không ghép một catalog lý tưởng từ nhiều phạm vi

Ma trận dùng chấm điểm phải thuộc **cùng một hồ sơ khả thi**. Không lấy chi phí thấp nhất từ q1 và khả năng bảo mật cao nhất từ q2 nếu không thể cùng áp dụng.

Đề xuất v1: mỗi catalog được chấm theo một hồ sơ tham chiếu khả thi đã công bố, chọn theo chính sách trước khi tính điểm và giữ nguyên trong phân tích độ nhạy. Nếu còn nhiều hồ sơ chưa có cơ sở chọn, trả các kết quả theo điều kiện, không tự gộp thành một hàng. Chỉ loại cả catalog khi đã xét hết phạm vi được phép trong mô hình.

Mở rộng sau có thể chấm mọi cặp khả thi rồi lấy điểm cao nhất của từng catalog theo chính sách tối ưu nội bộ. Khi trọng số thay đổi, hồ sơ tốt nhất có thể đổi; lúc đó điểm catalog là bao trên của nhiều hàm, không được áp dụng nguyên kiểm tra LP dành cho một hàng cố định.

## 4. Vấn đề 2 — Thang đo, trọng số và đánh giá đa tiêu chí

### 4.1. Tách phép đo khỏi giá trị

Ba tầng dữ liệu cần ghi riêng:

```text
Thuộc tính kỹ thuật/đại lượng của hồ sơ
  → mức đáp ứng mục tiêu của ca lựa chọn
  → giá trị mà người ra quyết định gán cho mức đó.
```

Ví dụ thiết kế: thời gian vận hành theo cùng workload là đại lượng; “ít công vận hành” là mục tiêu; giảm từ 20 xuống 10 giờ có đáng giá bằng giảm từ 10 xuống 0 giờ không là sở thích. KB có thể chứa đại lượng đúng nhưng chưa trả lời câu hỏi cuối.

Với tiêu chí lợi ích định lượng, có thể thử hàm:

\[
v_j(x)=\operatorname{clip}_{[0,1]}\frac{x-L_j}{U_j-L_j}.
\]

Với tiêu chí chi phí, đảo chiều tử số thành `U_j-x`. Đây là **giả định giá trị tuyến tính trong khoảng**, không phải chỉ đổi đơn vị. Các mốc phải có nghĩa, `U_j>L_j`, cùng bối cảnh; clipping đồng nghĩa không phân biệt các mức ngoài mốc, cần chấp nhận rõ. Có thể thay bằng hàm từng đoạn nếu mức cải thiện không có giá trị đều nhau.

Với ordinal/rubric 1–5, thứ tự không xác định khoảng cách. E04 dùng A=(5,1), B=(3,4), trọng số bằng nhau: cộng nhãn chọn B; một phép gán giá trị tăng nghiêm ngặt khác lại chọn A. Vì vậy phải hiệu chỉnh giá trị tại từng mức, hoặc giữ so sánh thứ bậc thay vì tự giả định thang khoảng.

Với boolean mềm, 0/1 có thể là hai mốc giá trị nếu người dùng chấp nhận khác biệt đó. Không tự cộng số engine hỗ trợ ngoài tập doanh nghiệp cần. Không dùng các nhãn “bảo mật cao”, “dễ vận hành” làm điểm nếu chưa định nghĩa mức đáp ứng quan sát được.

Đề xuất giữ mốc thang ổn định theo revision cho các phiên lựa chọn cần so sánh. E05 cho thấy min–max tính lại từ ứng viên có thể đảo A/B sau khi thêm C bị B trội: A=(8,2), B=(6,6), C=(0,5), weights=(0,6;0,4). Trước C: A=0,6 > B=0,4; sau C: A=0,6 < B=0,85. Đây là tác động đổi thang, không phải phát hiện C làm B tốt hơn về kỹ thuật.

### 4.2. Lấy trọng số từ đánh đổi có nghĩa

Nguồn phương pháp phân biệt trọng số gắn với **khoảng cải thiện trên thang giá trị**, kiểm tra tính độc lập ưu tiên và tránh đếm một lợi ích nhiều lần. Swing weighting là một cách thu thập các đánh đổi đó; không chỉ hỏi tên tiêu chí nào quan trọng hơn. [MCA manual, 2009, §5.4.4 và §§6.2.8–6.2.12](https://assets.publishing.service.gov.uk/media/5a790545e5274a2acd18b975/1132618.pdf)

Quy trình đề xuất:

1. Chỉ chọn các mục tiêu mềm có liên quan và có thang đã định nghĩa.
2. Mô tả hồ sơ tham chiếu ở mốc thấp; so các thay đổi lên mốc cao của từng mục tiêu bằng từ ngữ/đơn vị người dùng hiểu.
3. Thu đánh giá về các thay đổi; chuẩn hóa các mức quan trọng không âm thành tổng bằng 1.
4. Kiểm tra lại trên vài cặp hồ sơ có đánh đổi, thay vì chỉ kiểm tra tổng trọng số.
5. Lưu phản hồi, người xác nhận, thang giá trị và revision đi cùng bộ trọng số.

Các lựa chọn khi chưa có phần thu ưu tiên:

| Tình huống | Kết quả hợp lệ |
|---|---|
| Người dùng xác nhận thang và một vector trọng số | Ranking theo mô hình đã xác nhận |
| Người dùng chọn một preset và được xem nội dung preset | Ranking theo chính sách preset; không gọi là sở thích đo được của cả nhóm doanh nghiệp |
| Chỉ có thứ tự/giới hạn ưu tiên | Xét miền trọng số hợp lệ và quan hệ chắc chắn; có thể còn shortlist |
| Chưa có thông tin ưu tiên | Pareto và hồ sơ đánh đổi; equal weights chỉ là một kịch bản tham chiếu có nhãn |

Không dùng entropy/độ phân tán giữa catalog để thay cho sở thích doanh nghiệp. Dữ liệu phân biệt ứng viên mạnh chưa đồng nghĩa lợi ích đó quan trọng hơn. Nếu nhiều stakeholder bất đồng, giữ các kịch bản ưu tiên riêng trước khi áp dụng một quy tắc đồng thuận được thống nhất.

### 4.3. Khi nào Weighted Sum đủ dùng?

Với tập mục tiêu mềm J và hồ sơ khả thi a:

\[
V(a\mid u,w)=\sum_{j\in J}w_jv_j(a,u),\quad w_j\ge0,\quad\sum_{j\in J}w_j=1.
\]

Đề xuất dùng mô hình này khi: thang giá trị có nghĩa; đánh đổi được chấp nhận; các chiều giá trị đủ độc lập cho mô hình cộng; không đếm trùng lợi ích; cùng mục tiêu và cùng quy ước áp dụng cho các ứng viên. Chọn cách tổng hợp phải theo cấu trúc dữ liệu và sở thích, không theo thuật toán cho kết quả mong muốn. [Roy & Słowiński, 2013, Q1a–Q1e và Q2](https://link.springer.com/article/10.1007/s40070-013-0004-7)

Hai loại phụ thuộc khác nhau:

- **Phụ thuộc kỹ thuật:** hai tính năng phải hoạt động cùng nhau → kiểm tra ở miền khả thi.
- **Tương tác giá trị:** lợi ích của X tăng/giảm tùy mức Y → có thể làm mô hình cộng không phù hợp, dù mọi tổ hợp đều khả thi.

Ví dụ thiết kế: nếu TCO đã tính công nhân sự vận hành, không cộng lại toàn bộ lợi ích tiết kiệm cùng công đó vào tiêu chí effort. Một khả năng là dùng chi phí tiền dịch vụ và công vận hành thành hai chiều không chồng lấn; hoặc giữ TCO và chỉ đánh giá khía cạnh vận hành khác thực sự có giá trị riêng. Tương quan dữ liệu không tự chứng minh có hay không có đếm trùng.

| Vấn đề còn lại | Hướng xử lý trước | Khi cân nhắc phương pháp khác |
|---|---|---|
| Mức tối thiểu tuyệt đối không được bù | Đưa mức đó thành HARD; phần vượt mức chỉ là SOFT nếu có giá trị riêng | Không cần đổi thuật toán chỉ vì tồn tại mức sàn |
| Tiêu chí ưu tiên tuyệt đối theo thứ tự | Xác nhận thực sự không đánh đổi, kể cả chênh lệch rất nhỏ | Lexicographic nếu đúng ý nghĩa ưu tiên; không suy từ “quan trọng hơn” thông thường |
| Người dùng thuận tiện so sánh cặp | Có thể khảo sát AHP để lấy ưu tiên | AHP không tự xác nhận sự thật kỹ thuật hoặc chữa mọi tương tác giá trị |
| Không muốn tổng thứ hạng, cần quan hệ không phân định | Giữ shortlist/đánh đổi | Khảo sát outranking và xác nhận tham số của variant cụ thể |
| Tương tác giá trị không loại được bằng thiết kế tiêu chí | Thử gộp/tái cấu trúc các chiều trước | Nghiên cứu mô hình phi cộng như Choquet; cần thêm tham số và ca kiểm chứng |
| Ưu tiên chưa đủ | Giữ miền mô hình và hỏi/so sánh độ nhạy | ROR hoặc regret khi có câu hỏi nghiên cứu tương ứng |

AHP dùng so sánh cặp để suy ra ưu tiên; consistency không tự chứng minh mô hình lựa chọn đúng. [Saaty, 2008, abstract](https://doi.org/10.1504/IJSSCI.2008.017590). Việc dùng tham số phi cộng để thể hiện tương tác có nền tảng riêng, nhưng không có căn cứ phải thêm Choquet vào v1 này. [Angilella, Corrente & Greco, arXiv:1302.6192v2, §§1–2](https://arxiv.org/html/1302.6192v2)

Nếu không còn tiêu chí mềm, hoặc tất cả hồ sơ có cùng giá trị trên chúng, trả tập đủ điều kiện/hòa. Không tạo tiêu chí hoặc trọng số để ép ra một tên.

## 5. Vấn đề 3 — Độ nhạy, ổn định và giải thích

### 5.1. Phân tích đúng ví dụ người dùng gửi

Với A=(5,5,3), B=(3,5,5) theo ba chiều bảo mật, tích hợp, vận hành, **giả sử đây đã là giá trị khoảng hợp lệ**, ta có:

\[
S(A)-S(B)=2w_{security}-2w_{operations}.
\]

Bộ (0,40;0,35;0,25) cho A=4,50, B=4,20 đúng như đầu vào. Nếu đổi mốc 1→0, 5→1 bằng `v=(s-1)/4`, V(A)=0,875, V(B)=0,800. Đây là giá trị theo mô hình, không phải 87,5% và 80% yêu cầu doanh nghiệp được thỏa mãn.

Giữ trọng số tích hợp 0,35 và chỉ chuyển trọng số giữa bảo mật/vận hành: hòa tại **0,325;0,35;0,325**. Cần chuyển **7,5 điểm phần trăm** từ bảo mật sang vận hành để hòa; chuyển nhiều hơn thì B thắng. Đây là ranh giới cho đúng đường thay đổi đã nêu, không phải bán kính ổn định trên mọi thay đổi có thể có. E03 đã kiểm tra bằng phân số chính xác.

### 5.2. Xét nhiều trọng số cùng lúc

Với các hàng giá trị cố định, đặt W là miền trọng số có căn cứ và không rỗng; có thể gồm giới hạn từng trọng số, tổng bằng 1 và các phản hồi so sánh. Tính cho mỗi đối thủ b:

\[
L_{ab}=\min_{w\in W}\sum_jw_j[v_j(a)-v_j(b)],\qquad
H_{ab}=\max_{w\in W}\sum_jw_j[v_j(a)-v_j(b)].
\]

Nếu mọi L_ab ≥ 0, a luôn ít nhất tốt bằng mọi đối thủ trong W. Nếu có L_ab < 0 thì có kịch bản làm a thua b; không đồng nghĩa a thường thua. Với W là đa diện và v cố định, đây là LP; không cần giả định phân phối xác suất. Đây là trường hợp hạn chế của cách xét các mô hình giá trị tương thích trong ROR, không phải toàn bộ UTA-GMS. [Greco et al., 2008, §4.3](https://www.lamsade.dauphine.fr/mcda/biblio/PDF/GMS-EJOR2008.pdf)

E06 tính chính xác trên các đỉnh của hai miền minh họa, với giá trị đã đổi về [0,1]:

| Miền giả định, luôn kèm tổng trọng số = 1 | Khoảng V(A)−V(B) | Diễn giải |
|---|---|---|
| Security [0,36;0,44], integration [0,31;0,39], operations [0,21;0,29] | [0,035;0,115] | A thắng trong toàn miền này |
| Security [0,25;0,45], integration [0,30;0,40], operations [0,20;0,40] | [−0,075;0,125] | Có trọng số làm A thắng, có trọng số làm B thắng |

Các khoảng này chỉ phục vụ ví dụ, không phải mức ±% mặc định được đề xuất cho doanh nghiệp. Cần xét ràng buộc tổng, không thay đồng thời các đầu mút tạo vector không hợp lệ. Nếu W rỗng, giải thích phản hồi bất tương thích trước khi ranking.

### 5.3. Phân biệt sensitivity, SMAA và regret

- **Sensitivity:** chỉ ra thay đổi nào làm kết quả đổi; có thể dùng đường thay đổi hoặc cả miền W.
- **SMAA:** dùng phân phối trên tham số để tính mức chấp nhận thứ hạng; tỷ lệ thắng khi lấy mẫu phụ thuộc phân phối và quy ước hòa. KB chính xác vẫn cho phép phân tích trọng số không chắc chắn. [Angilella et al., v2, §3](https://arxiv.org/html/1302.6192v2)
- **Minimax regret:** chọn theo tổn thất cơ hội lớn nhất thấp nhất khi sở thích chưa xác định đủ; là chính sách quyết định, không phải xác suất chọn sai. [Boutilier et al., 2006, §3](https://www.cs.toronto.edu/~cebly/Papers/BPPS-aij06.pdf)

Đề xuất v1: sensitivity xác định và shortlist khi ưu tiên chưa đủ. Không gọi mô phỏng tự đặt là “SMAA-lite” nếu chưa đặc tả phân phối, miền lấy mẫu, seed/sai số và cách tính thứ hạng. Không dùng tỷ lệ thắng trên trọng số ngẫu nhiên làm “độ chính xác” của khuyến nghị.

### 5.4. Giải thích phải tái tạo được phép tính

Mỗi kết quả cần bốn phần:

1. **Tư cách:** điều kiện bắt buộc và hồ sơ chứng minh cùng đáp ứng; vì sao loại các catalog khác.
2. **Giá trị:** thuộc tính → hàm giá trị → trọng số → đóng góp; nguồn của thang và ưu tiên.
3. **So sánh trực tiếp:** với a và b, hiển thị `d_j = w_j(v_j(a)-v_j(b))`; tổng d_j bằng chênh lệch điểm.
4. **Độ nhạy và giới hạn:** miền đã kiểm tra, ranh giới đổi lựa chọn, snapshot/rule revision, phần input chưa rõ.

Trong E03 theo [0,1], A hơn B về bảo mật +0,200, hòa về tích hợp 0,000, kém về vận hành −0,125; tổng +0,075. “Bảo mật có trọng số cao” riêng lẻ chưa giải thích đủ; cần cả mức chênh lệch giá trị.

Trọng số bằng 0 có thể làm phương án bị trội vẫn hòa điểm; E07 kiểm tra điều này. Giữ thông tin Pareto và công bố quy tắc phá hòa nếu cần, không âm thầm xóa mọi phương án hòa. Phân biệt dung sai số học với ngưỡng khác biệt người dùng coi là đáng kể.

ADR là bản ghi quyết định: bối cảnh, ứng viên, mô hình/ưu tiên, khuyến nghị hoặc tập hòa, lý do, điều kiện và hệ quả. Tạo được ADR không chứng minh khuyến nghị đúng. Nếu có LLM, chỉ diễn đạt kết quả đã tính; mẫu cố định đủ dùng cho v1.

## 6. Không có ứng viên — tìm xung đột và sửa chữa đúng nghĩa

Giữ bối cảnh cố định D và oracle `SAT(S) = F(S,u) không rỗng`.

- **Tập xung đột tối thiểu theo bao hàm:** M không có nghiệm; bỏ bất kỳ một yêu cầu nào khỏi M thì có nghiệm. Không đồng nghĩa ít phần tử nhất.
- **Tập sửa chữa:** R là nhóm yêu cầu được phép bỏ/sửa để **toàn bộ tập còn lại** có nghiệm. Phải chạy lại oracle trên toàn bộ tập đó.

QuickXplain tìm xung đột theo quan hệ nhất quán đơn điệu, với các ràng buộc nền không được nới. Không được diễn giải “tìm một conflict” thành “đã tìm cách sửa toàn bộ yêu cầu”. [Junker, AAAI 2004, pp.167–170](https://cdn.aaai.org/AAAI/2004/AAAI04-027.pdf)

E02 có ba yêu cầu H1,H2,H3; mỗi ứng viên chỉ thỏa một yêu cầu. Mỗi cặp là một conflict. Bỏ H1 khỏi conflict {H1,H2} vẫn để H2,H3 không có nghiệm. Muốn có nghiệm phải bỏ hai yêu cầu trong ví dụ này.

Đề xuất v1: duyệt/bỏ dần yêu cầu để tìm một conflict dễ kiểm tra; với ít điều kiện, liệt kê các tập sửa được phép rồi kiểm tra toàn bộ tập còn lại. Nếu số lượng lớn mới cần chiến lược tối ưu/hitting set. “Ít thay đổi nhất”, “ít điều kiện nhất” và “chi phí đổi thấp nhất” là ba mục tiêu khác nhau; chỉ dùng chi phí sửa khi đã có mô hình chi phí.

Khi thử giảm ngưỡng hoặc đổi HARD thành SOFT, gắn nhãn phản thực và yêu cầu mới phải được xác nhận trước khi thành quyết định chính thức. Nếu các điều kiện gây bất khả thi đều không được phép đổi, trả “không có ứng viên trong phạm vi xét”. Không sửa sự thật KB để tạo lời giải.

## 7. Pipeline đề xuất sau nghiên cứu

```text
Form đã chốt + bối cảnh + chính sách ưu tiên
  → Chuẩn hóa HARD / SOFT / CONTEXT; kiểm tra input đủ xác định
  → Tìm hồ sơ cùng thỏa các ràng buộc và quan hệ miền
      ├─ Không có: conflict + sửa chữa giả định được phép
      └─ Có: ma trận hiệu năng theo hồ sơ nhất quán
          → Thang giá trị và mô hình ưu tiên hợp lệ?
              ├─ Có: Weighted Sum → hòa/thứ hạng
              └─ Chưa: Pareto/miền trọng số → shortlist hoặc làm rõ ưu tiên
          → Giải thích + sensitivity + ADR
```

Pareto có thể tính như kiểm tra bổ trợ trên cùng các chiều giá trị, không cần là tầng lọc riêng. Không cho một điểm mềm lớn bù điều kiện bắt buộc; E08 kiểm tra trường hợp này.

**Vị trí ba lớp:** facts/phạm vi ở lớp 1; mapping form–yêu cầu ở lớp 2; feasibility, giá trị, ưu tiên và giải thích quyết định ở lớp 3. Chấm “phù hợp doanh nghiệp” không trở thành fact phổ quát trong lớp 1. Preset và hàm giá trị là chính sách quyết định có revision.

Nếu còn input chưa rõ: trả `INPUT_INCOMPLETE`. Nếu evaluator chưa hỗ trợ hoặc solver chưa kết luận: trả trạng thái thực thi chưa hoàn tất. Hai trạng thái này khác với thiếu bằng chứng công nghệ và khác với `INFEASIBLE` đã chứng minh. Giả định KB đầy đủ không làm mất các phân biệt đó.

## 8. Kiểm chứng: điều gì có thể và chưa thể chứng minh?

### 8.1. Tách ba câu hỏi đánh giá

| Tầng | Phép đánh giá đề xuất | Kết luận cho phép |
|---|---|---|
| Logic/formal | Oracle độc lập hoặc duyệt hết miền nhỏ; phản ví dụ; kiểm tra thuộc tính | Bộ kiểm tra/điểm/giải thích đúng với mô hình trên tập ca đã kiểm tra |
| Giá trị của mô hình | Người ra quyết định đánh giá các đánh đổi; kiểm tra trên cặp/ca chưa dùng để hiệu chỉnh | Mô hình phản ánh ưu tiên ở mức đã quan sát |
| Hữu ích khi dùng | So với đọc báo cáo/chọn thủ công, cùng KB và bối cảnh | Hiệu quả hỗ trợ trong mẫu, không phải catalog tối ưu cho mọi tổ chức |

### 8.2. Thiết kế đối chứng để cô lập nguyên nhân

Đóng băng cùng KB, tập công nghệ, mapping, rubric và phân chia ca phát triển/ca đánh giá; chỉ thay phần được nghiên cứu:

- **B0:** kiểm tra từng tính năng độc lập → làm đối chứng cho bộ kiểm tra kết hợp. Không dùng như hệ khuyến nghị hoàn chỉnh.
- **B1:** lọc kết hợp + equal weights có nhãn → đối chứng cho việc thu sở thích.
- **B2:** lọc kết hợp + mô hình giá trị/trọng số đã xác nhận → phương pháp đề xuất.
- **B3:** lọc kết hợp + Pareto/đánh đổi → đối chứng cho nhu cầu ranking số khi sở thích chưa đủ.

Đánh giá riêng “thêm sensitivity có giúp người dùng hiểu và phát hiện kết quả mong manh không”; sensitivity tự nó không làm sở thích ban đầu đúng hơn. Khi so B1 và B2 trên cùng ca, giữ nguyên thang giá trị để cô lập tác động của trọng số. Nếu thay cả thang, báo đó là thí nghiệm khác.

### 8.3. Ca và chỉ số cần có

| Nhóm ca | Điều cần kiểm tra |
|---|---|
| Vi phạm HARD nhưng điểm mềm cao | Không được đề xuất ứng viên không khả thi |
| Tính năng riêng lẻ đúng nhưng tổ hợp sai | Phát hiện lỗi AND các ô hỗ trợ hoặc trộn phạm vi |
| Nhiều conflict, yêu cầu không được nới | Conflict đúng; sửa chữa phải thật sự khôi phục tính khả thi và giữ điều kiện được bảo vệ |
| Không có hoặc không phân biệt được tiêu chí mềm | Trả tập hòa/shortlist |
| Ordinal và đổi mốc chuẩn hóa | Không đưa thêm giả định về khoảng cách/thang mà không công bố |
| Thay thứ tự ứng viên/câu trả lời | Không đổi kết quả nếu mô hình và dữ liệu không đổi |
| Tăng giá trị một chiều với các chiều khác giữ nguyên | Điểm không giảm khi trọng số không âm; nếu giá trị không đổi sau clipping thì điểm có thể giữ nguyên |
| Thêm phương án bị trội, giữ thang và chính sách cố định | Không đổi chênh lệch điểm cũ; không tự áp invariant này cho thuật toán có chính sách phụ thuộc tập ứng viên |
| Gần ranh giới, trọng số 0, W rỗng | Hòa/không ổn định/bất tương thích được báo đúng |
| Input chưa xác định, evaluator lỗi/timeout | Không kết luận không khả thi hoặc tương thích chỉ vì chưa tính xong |

Chỉ số đề xuất: tỷ lệ đề xuất vi phạm HARD (ghi số ca và mẫu số), độ đúng feasibility so oracle, tính đúng/tối thiểu theo bao hàm của conflict, tỷ lệ sửa chữa thực sự khả thi, tỷ lệ cặp ưu tiên ngoài tập hiệu chỉnh được mô hình tái hiện, mức bao phủ giải thích và thời gian/công sức quyết định. Với chuyên gia, lưu tập lựa chọn chấp nhận được và bất đồng, không áp một tên làm “chân lý”. Báo riêng ca không đồng thuận; không đồng nhất việc mở rộng oracle bằng hợp tất cả ý kiến với đồng thuận cao.

Mục tiêu logic là không vi phạm điều kiện bắt buộc; quan sát 0 lỗi trên một tập ca không chứng minh 0 lỗi ngoài mẫu. Số ca, số người và ngưỡng chấp nhận phải dựa vào thiết kế nghiên cứu/nguồn lực; chưa có căn cứ ấn định “đạt 90%” hoặc một cỡ mẫu bảo đảm. Benchmark tải thật chỉ cần khi kiểm tra giả định KB hoặc năng lực triển khai; không phải điều kiện tiên quyết để so hai thuật toán lựa chọn dưới cùng ma trận đã cho.

### 8.4. Kết quả đã làm trong lượt này

[Script](complete-kb-checks.py) dùng thư viện chuẩn Python và `fractions.Fraction`; [kết quả](complete-kb-check-results.json) lưu số hữu tỉ chính xác và dạng thập phân. Tám ví dụ E01–E08 kiểm tra các phản ví dụ và phép tính trong tài liệu. Chúng là **kiểm tra ví dụ nghiên cứu**, không đo chất lượng quyết định của sản phẩm hoặc xác minh tính năng catalog.

Chạy: `python system-selection/research/catalog-knowledge-base/complete-kb-checks.py` từ workspace. Script ghi lại JSON kết quả cạnh chính nó.

## 9. Nguồn và phạm vi đã đọc

Đây là tổng quan tập trung theo vấn đề người dùng gửi, không phải systematic review hay so sánh thực nghiệm mọi phương pháp MCDM. Không cần nguồn mới nhất để thay các định nghĩa nền tảng; ngày trên bản lập chỉ mục không được dùng thay năm công bố.

| Nguồn gốc | Phần đã đối chiếu trong lượt này | Dùng cho / giới hạn |
|---|---|---|
| [Farshidi et al., 2018, Journal of Decision Systems, DOI 10.1080/12460125.2018.1464821](https://slingerjansen.nl/wp-content/uploads/2018/05/a-decision-support-system-for-software-technology-selection.pdf) | Mở toàn văn PDF; đọc chọn lọc abstract, §4 và inference engine | Tiền lệ tách feasibility/ranking; không chuyển bộ features hoặc kết quả DBMS sang catalog |
| [Dodgson et al., MCA manual, DCLG 2009](https://assets.publishing.service.gov.uk/media/5a790545e5274a2acd18b975/1132618.pdf) | §5.4.4 và các đoạn §§6.2.8–6.2.12 qua PDF text, đối chiếu với phiếu nghiên cứu MCDA cũ | Chuẩn hóa thang giá trị, swing, độc lập ưu tiên; tài liệu hướng dẫn, không phải benchmark phương pháp catalog |
| [Roy & Słowiński, 2013, DOI 10.1007/s40070-013-0004-7](https://link.springer.com/article/10.1007/s40070-013-0004-7) | Q1a–Q1e/Q2 qua bài và tìm đoạn; chú trọng Q1e | Chọn họ phương pháp theo bài toán, tương tác; không đặc tả đủ một variant outranking để triển khai |
| [Junker, QuickXplain, AAAI 2004, pp.167–172](https://cdn.aaai.org/AAAI/2004/AAAI04-027.pdf) | Phần mở đầu, định nghĩa conflict/relaxation và điều kiện oracle pp.167–170 | Phân biệt giải thích/sửa chữa, tính đơn điệu; thuật toán và runtime chưa được triển khai ở đây |
| [Boutilier et al., Artificial Intelligence 170, 2006, pp.686–713](https://www.cs.toronto.edu/~cebly/Papers/BPPS-aij06.pdf) | Abstract, đầu bài và đối chiếu nghiên cứu regret trước | Sở thích chưa đầy đủ vẫn tạo bài toán regret; không lặp lại thực nghiệm tác giả |
| [Angilella, Corrente & Greco, arXiv:1302.6192v2, 2013](https://arxiv.org/html/1302.6192v2) | Abstract và §§1–3, nhất là định nghĩa phân phối/thứ hạng SMAA-2 | Nguồn nghiên cứu mở rộng SMAA/Choquet; không nói đã đọc toàn bộ thí nghiệm hoặc bài gốc SMAA 1998 |
| [Greco, Mousseau & Słowiński, EJOR 191, 2008, pp.415–435](https://www.lamsade.dauphine.fr/mcda/biblio/PDF/GMS-EJOR2008.pdf) | §4.3–4.4, đối chiếu phiếu ROR cũ | Quan hệ cần thiết/có thể và ưu tiên bất tương thích; miền trọng số cố định là một trường hợp hạn chế |
| [Saaty, 2008, DOI 10.1504/IJSSCI.2008.017590](https://doi.org/10.1504/IJSSCI.2008.017590) | Metadata và abstract; đường mở PDF toàn văn lỗi trong lượt này | Chỉ dùng cho vai trò so sánh cặp của AHP; chưa thẩm định một thiết kế AHP cho đề tài |

## 10. Phạm vi thực hiện được đề xuất

**Lõi nên thử:** requirement mapping có revision; bộ kiểm tra tổ hợp; hồ sơ giá trị nhất quán; Weighted Sum khi đủ thông tin ưu tiên; phân tích điểm đổi thứ hạng; giải thích có thể tính lại; bộ ca đối chứng.

**Chưa cần đưa vào lõi:** SMAA, minimax, Choquet hoặc solver tổng quát. Giữ chúng như hướng mở rộng theo vấn đề chưa giải quyết được, không loại bỏ vì nhầm rằng KB hoàn hảo đồng nghĩa biết hết sở thích.

Đóng góp có thể kiểm chứng của đề tài là mô hình yêu cầu catalog có quan hệ kết hợp, cách thu và biểu diễn giá trị, tính đúng của cơ chế quyết định và kết quả đánh giá trên ca mới. Việc ghép các thuật toán đã tồn tại chưa tự chứng minh tính mới hoặc chất lượng khuyến nghị.
