# Công nghệ cho MVP hỗ trợ lựa chọn lakehouse catalog

Ngày đối chiếu tài liệu: **17/10/2026**.

Đây là nghiên cứu công nghệ và đề xuất triển khai, chưa xây ứng dụng, cài dependency hoặc đo hiệu năng. Các quyết định kiến trúc bên dưới là khuyến nghị cho bài toán của người dùng; tính năng thư viện được đối chiếu tài liệu chính thức. Không xác nhận lại tính đúng của các claim về catalog trong lượt này.

## 1. Đề xuất chính

**Lõi Python độc lập + FastAPI + React/TypeScript qua Vite + KB JSON có phiên bản + pytest/Hypothesis.** SQLite chỉ thêm khi cần lưu các lần đánh giá. Dùng hàm Python và duyệt hữu hạn cho luật, khoảng điểm, regret và sửa chữa yêu cầu; chưa cần một rule engine hoặc solver tổng quát.

Nếu mục tiêu trước mắt chỉ là demo phương pháp bằng một ngôn ngữ, dùng **Streamlit gọi trực tiếp cùng lõi Python**. Chỉ chọn một giao diện cho giai đoạn đầu; không xây cả Streamlit và React cùng lúc.

Căn cứ lựa chọn từ tài liệu đang có:

- [README KB](README.md) ghi mục đích đồ án/nghiên cứu, prototype và website từ form; LLM không bắt buộc.
- [Input v1](input-v1.md) đã có bộ hỏi, còn giới hạn về thao tác engine, storage và streaming.
- [Lớp 1 v2](layer-1-design.md) dùng `scopes`, `properties`, `claims` và evidence nhúng; không cần đổi sang graph database.
- [Ví dụ Python](complete-kb-checks.py) đã có hàm dot product, duyệt tập con và kiểm tra phạm vi kết hợp. Đây là tài liệu tham chiếu và nguồn test case; chưa phải engine để đưa nguyên vào web.
- Bản nháp mới nhất của người dùng là hướng thiết kế mới. Không tự sửa lại input v1 hoặc các tài liệu phương pháp trước để giả rằng mọi thay đổi đã được chốt.

## 2. So sánh các phương án công nghệ

| Phương án | Phù hợp khi | Đánh đổi | Quyết định đề xuất |
|---|---|---|---|
| Streamlit + Python | Muốn chứng minh phương pháp sớm; chủ yếu biết Python | Luồng rerun/session và các trường phụ thuộc nhau cần chú ý; ít tự do giao diện hơn SPA | Đường ngắn nhất cho demo nội bộ |
| React + Vite + FastAPI | Cần website cho người dùng thử form, so sánh và mở lý do chi tiết | Hai môi trường Python/Node, thêm hợp đồng API và kiểm thử giao diện | Hướng chính cho MVP web của đề tài |
| Toàn bộ TypeScript | Đã thành thạo TypeScript, muốn dùng một runtime | Phải chuyển các ví dụ và bộ đánh giá Python; lợi ích tái sử dụng nghiên cứu hiện tại thấp hơn | Chỉ ưu tiên nếu kỹ năng hiện có nghiêng rõ về TypeScript |
| Rule engine/DMN hoặc SMT solver làm lõi ngay | Luật lớn, cần người không viết code biên soạn hoặc nhiều phụ thuộc logic phức tạp | Thêm mô hình biểu diễn và công giải thích; không thay thế thiết kế giá trị/tri thức | Để sau khi đo được giới hạn lõi đơn giản |

Streamlit hỗ trợ `st.form` gom input để gửi khi submit; widget phụ thuộc nhau trong cùng form chỉ cập nhật khi submit. Đây là giới hạn có liên quan trực tiếp nếu engine hoặc format làm thay đổi các lựa chọn khác. [Tài liệu Streamlit](https://docs.streamlit.io/develop/concepts/architecture/forms)

FastAPI cung cấp OpenAPI, tài liệu API tương tác và tích hợp Pydantic. Vite có template `react-ts`. Những khả năng này hỗ trợ tách UI khỏi engine; chúng không tự kiểm chứng tính đúng của luật quyết định. [FastAPI](https://fastapi.tiangolo.com/features/), [Vite](https://vite.dev/guide/)

## 3. Stack và trách nhiệm từng thành phần

| Thành phần | Công nghệ | Trách nhiệm |
|---|---|---|
| Form, bảng so sánh, mở bằng chứng | React + TypeScript + Vite | Thu thập input và hiển thị kết quả server; không tự tính lại ranking |
| API | FastAPI | Validate request, gọi engine, trả response có cấu trúc |
| Hợp đồng dữ liệu | Pydantic | Kiểu input, requirement, claim, scenario, assessment, trace |
| Cơ sở tri thức | JSON trong Git | Lớp 1: sự thật; lớp 2: mapping; lớp 3: chính sách đánh giá |
| Bộ suy luận | Python thuần | Gate, scope matching, giá trị, scenario, chẩn đoán, giải thích |
| Lịch sử đánh giá, nếu cần | SQLite qua `sqlite3` | Lưu snapshot input/output và phiên bản dùng để tái lập |
| Kiểm thử | pytest + Hypothesis | Ca cụ thể, thuộc tính, phản ví dụ và kiểm tra bất biến |
| Đóng gói | Dependency lockfile; Docker khi cần chia sẻ môi trường | Tái lập môi trường chạy, không phải một tầng suy luận |

Pydantic mặc định có thể ép kiểu; nên chủ động dùng strict validation ở các trường số/boolean cần phân biệt rõ và cấm field thừa ở hợp đồng chính. Chọn cách parse enum/JSON nhất quán thay vì bật strict toàn cục mà chưa kiểm tra hành vi. [Strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)

SQLite phù hợp lưu trữ cục bộ phía server, nhưng chỉ cho một writer tại một thời điểm. Khi cần nhiều instance ghi chung hoặc tải ghi đồng thời lớn, cân nhắc PostgreSQL. Chưa cần thêm ORM và migration framework chỉ để lưu vài snapshot. [SQLite: trường hợp sử dụng](https://www.sqlite.org/whentouse.html)

Các quyết định còn lại về chart library, CSS và ORM có thể để sau một lát cắt chạy được; chúng không quyết định tính hợp lệ của phương pháp.

## 4. Kiến trúc tối thiểu

```text
React form
    │ POST /evaluate
    ▼
FastAPI / Pydantic
    ▼
decision_core.evaluate(input, knowledge, policy)
    ├─ normalize: câu trả lời → HARD / SOFT / CONTEXT
    ├─ resolve: chọn claim và scope áp dụng
    ├─ enumerate: sinh các kịch bản điền hợp lệ
    ├─ assess: gate → giá trị → điểm trong từng kịch bản
    ├─ diagnose: xung đột và đề xuất nới giả định
    ├─ analyze: khoảng, so sánh cặp, regret, thông tin cần làm rõ
    └─ explain: trace → mẫu câu có cấu trúc
    ▼
Kết quả JSON → bảng/biểu đồ/lý do trên UI
    └─ SQLite snapshot, nếu bật lưu lịch sử
```

Lõi không import FastAPI, Streamlit hoặc database. Có thể chạy một fixture từ CLI, notebook, test suite và web bằng cùng một hàm. Giao diện không truy cập trực tiếp DB.

API khởi đầu chỉ cần:

- `GET /questionnaire`: câu hỏi, lựa chọn và revision; không bắt buộc xây trình sinh form tổng quát.
- `POST /evaluate`: đánh giá và trả kết quả; việc lưu lịch sử là tùy chọn rõ ràng.
- `GET /evaluations/{id}`: chỉ thêm khi đã có lưu lịch sử.

Tất cả nghiệp vụ chạy đồng bộ trong v1 nếu nằm trong ngân sách thời gian đã đo; chưa cần queue/worker. Request vượt giới hạn tính toán phải trả trạng thái rõ, không âm thầm tính một phần rồi gắn nhãn chính xác.

## 5. Dữ liệu và luật: giữ ba lớp nhưng dùng ít cơ chế

```text
knowledge/
  facts.json       # scopes, properties, claims, evidence
  mappings.json    # answer → requirement, rule_id, source_question_id
  policy.json      # value functions, weight presets, tie/unknown policies
```

Kế thừa mô hình lớp 1 đang có. Thêm tối thiểu vào lớp 2–3:

| Record | Trường cần giữ |
|---|---|
| Requirement | `id`, `source_question_id`, `kind`, `predicate_id`, `arguments`, `relaxable`, `mapping_rule_id` |
| Criterion | `id`, mức kỹ thuật hợp lệ, ánh xạ sang giá trị, lý do/phiên bản ánh xạ |
| Scenario | `id`, các câu trả lời điền giả định và điều kiện nhất quán |
| Assessment | catalog/scope, requirement, trạng thái, claim IDs, lý do và giả định |
| Evaluation | input, kết quả, KB/mapping/policy revision, engine revision, chế độ exact/approximate |

Luật lớp 2 có thể là bảng JSON nhỏ với toán tử whitelist như `eq`, `in`, `all`, `any`, gọi các hàm predicate đã đăng ký. Không dùng `eval`, không nhận Python expression từ trình duyệt. Các phép toán khó giữ trong hàm Python có test; chưa cần tự xây ngôn ngữ luật đầy đủ.

Giải thích đi theo chuỗi **câu trả lời → mapping rule → requirement → claim/scope → gate/đóng góp điểm → kết luận**. Dùng template và dữ liệu engine để viết lý do. Điều này cho phép kiểm tra từng câu giải thích có căn cứ nào mà chưa cần LLM.

KB JSON là nguồn chuẩn được review qua Git. SQLite lưu các lần chạy, không tạo một bản KB thứ hai phải đồng bộ. Revision phải trỏ tới nội dung còn truy xuất được; lưu hash đơn độc không đủ tái lập nếu nội dung cũ bị mất. Cách đơn giản: lưu snapshot của bundle nhỏ cùng lần chạy, kèm hash và engine revision.

## 6. Công nghệ/thuật toán cho từng đầu ra

### 6.1. Phân nhóm ứng viên

Với input đầy đủ và một scope nhất quán, một HARD thất bại sẽ loại scope đó. Catalog còn được giữ nếu có scope hợp lệ khác đáp ứng toàn bộ yêu cầu; không ghép các khả năng ở các scope loại trừ nhau.

Khi input thiếu, đánh giá trên các kịch bản hợp lệ:

- **Đủ điều kiện theo mô hình:** đáp ứng HARD ở mọi kịch bản được xét.
- **Phù hợp nếu…:** đáp ứng ở một phần kịch bản; ghi chính xác điều kiện nào làm thay đổi tính khả thi.
- **Không phù hợp trong phạm vi xét:** không có kịch bản và scope đang xét nào đáp ứng toàn bộ HARD.

Quy định rõ cách gộp scope về catalog; cùng một kịch bản phải dùng một cấu hình nhất quán cho mọi requirement. Đầu ra vẫn là catalog, scope là dấu vết giải thích điều kiện áp dụng.

Phân biệt ba tình trạng: thiếu input, thiếu claim và không có cấu hình khả thi. Giả định bỏ kiểm chứng KB không làm KB minh họa hiện tại trở thành đầy đủ. Có thể dùng fixture tổng hợp đầy đủ để kiểm tra logic, tách khỏi claim thực đang biên soạn.

### 6.2. Weighted Sum và khoảng

Giữ công thức đơn giản: `S(c, ω) = Σ w_j(ω) × v_j(c, ω)`, trong đó `ω` là một kịch bản hợp lệ, trọng số không âm và tổng bằng 1.

- Dùng hàm giá trị có neo tuyệt đối; không min–max theo tập catalog đang hiển thị.
- Bậc `Quan trọng/Nên có` ánh xạ qua một preset có phiên bản; tỷ lệ trọng số là giả định thiết kế cần hiệu chỉnh, không phải chân lý suy ra từ nhãn.
- `Bắt buộc` thành gate; không vừa là gate vừa được thưởng điểm trùng cùng lợi ích, trừ khi đã mô tả phần giá trị vượt ngưỡng riêng.
- Nếu không có tiêu chí mềm có trọng số, trả shortlist và lý do; không chia cho 0 hoặc bịa ranking.
- Khoảng là min/max điểm trên các kịch bản hợp lệ mà ứng viên đủ điều kiện; nếu chỉ khả thi có điều kiện, gắn nhãn đó ngay cạnh khoảng.
- Khoảng không phải confidence interval hoặc phần trăm xác suất phù hợp.

Điểm thứ bậc có mô tả neo vẫn chưa xác lập khoảng cách giá trị. Ví dụ `none/partial/full` cần ánh xạ giá trị riêng; `0/0.5/1` chỉ là một chính sách thử nghiệm. Kiểm tra thêm các ánh xạ tăng đơn điệu khác để xem kết luận có phụ thuộc quá mạnh vào giả định này không. Vấn đề này đã được minh họa trong [phương pháp với KB đầy đủ](complete-kb-selection-method.md).

### 6.3. Duyệt kịch bản

`itertools.product` sinh tích các miền hữu hạn, `combinations` sinh tập con phục vụ sửa chữa. Đây là khả năng sẵn có của Python. [Tài liệu itertools](https://docs.python.org/3/library/itertools.html)

Đề xuất v1:

1. Chỉ tạo miền cho trường chưa biết và thực sự ảnh hưởng các luật đang hoạt động.
2. Dùng cùng một câu trả lời giả định cho mọi tiêu chí và catalog liên quan; không cho cùng một tổ chức vừa có hai storage khác nhau chỉ để lấy cực trị đẹp.
3. Loại tổ hợp trái điều kiện phụ thuộc.
4. Giữ đầy đủ tập kịch bản trong phạm vi hữu hạn đã công bố, tính gate và điểm trong cùng lượt chạy.
5. Lưu số kịch bản được sinh, loại, đánh giá và trạng thái hoàn tất.

Kích thước là tích số lựa chọn của các biến chưa biết, không phải chỉ số catalog. Ví dụ 10 biến ba giá trị tạo 59.049 tổ hợp trước pruning. Biến đa chọn có thể lớn hơn nhiều. Đề xuất giới hạn nghiên cứu ban đầu 4–6 biến chưa biết liên quan quyết định, mỗi biến 2–3 giá trị; đây là phạm vi thiết kế, chưa phải kết luận hiệu năng.

Khi vượt ngân sách đo được: báo chưa hoàn tất hoặc chuyển sang chế độ xấp xỉ công khai. Min/max quan sát từ mẫu không phải bao chính xác của toàn miền; không gắn nhãn robust chỉ vì các mẫu chưa tìm thấy phản ví dụ. Miền liên tục cần phép tối ưu/bound riêng; không gọi duyệt lưới là duyệt mọi giá trị.

### 6.4. Tỷ lệ thắng và regret

Tính các ứng viên đủ HARD trong từng kịch bản trước khi xét điểm. Thống kê riêng số kịch bản không có ứng viên, số kịch bản ứng viên khả thi, thắng duy nhất và đồng hạng. Dùng chính sách tie có phiên bản.

Tỷ lệ thắng theo đếm kịch bản mô tả mức bao phủ trong tập kịch bản đã định nghĩa, không phải xác suất chọn đúng. Cách chia miền thành nhiều mức có thể làm đổi tỷ lệ; không diễn giải nó là độ tin cậy thực nghiệm.

Với ứng viên khả thi trong mọi kịch bản, regret trong một kịch bản là chênh lệch giữa điểm cao nhất của ứng viên khả thi và điểm của nó. Worst-case regret là max chênh lệch đó trên các kịch bản có lựa chọn. Không gán điểm 0 rồi trộn ứng viên vi phạm HARD vào phép tính. Ứng viên khả thi có điều kiện chỉ có regret có điều kiện và phải hiển thị phạm vi; không đặt cạnh regret toàn miền như hai đại lượng tương đương.

Khoảng điểm chồng nhau chưa chứng minh không có thứ tự chắc chắn: so trực tiếp chênh lệch điểm cặp catalog trong cùng từng kịch bản. Giữ kết quả đồng hạng/chưa phân biệt được khi dữ liệu không hỗ trợ thứ tự duy nhất.

### 6.5. Xung đột và gợi ý nới yêu cầu

Với số HARD nhỏ, dùng duyệt tập con và một hàm kiểm tra khả thi:

- Tìm một tập xung đột tối thiểu theo bao hàm bằng bỏ dần yêu cầu và kiểm tra lại.
- Tìm tập nới bằng duyệt các yêu cầu `relaxable`, theo số phần tử tăng dần; luôn kiểm tra **toàn bộ phần yêu cầu còn lại**.
- Giữ các yêu cầu nền không được nới; gợi ý là giả định để xem xét, không tự sửa input người dùng.
- Khi dữ liệu chưa rõ, phân biệt sửa chữa khôi phục khả thi ở mọi kịch bản với sửa chữa chỉ có nghiệm trong một số điều kiện.
- Nếu chặn số tập con hoặc số kết quả, ghi rõ chưa tìm hết; không tuyên bố sửa chữa tối ưu toàn cục.

Ví dụ 12 yêu cầu có 4.096 tập con; đây là số tổ hợp, không phải benchmark chạy. Khi số biến/luật tăng, thử Z3 với assumptions và unsat cores. Z3 có hướng dẫn liệt kê minimal unsatisfiable cores và maximal satisfying subsets. Một core lấy ra thông thường chưa tự đảm bảo ít phần tử nhất, và core không tự là tập sửa chữa. [Z3 Guide](https://microsoft.github.io/z3guide/programming/Example%20Programs/Cores%20and%20Satisfying%20Subsets/)

### 6.6. Thông tin nào đáng làm rõ

Không cần một agent hỏi đáp. Sau một lần submit, chia tập kịch bản theo từng câu hỏi chưa biết và các câu trả lời khả dĩ, rồi chạy lại phần tổng hợp trên từng nhánh.

Đề xuất ưu tiên theo: làm rõ tính khả thi của HARD, phân biệt quan hệ thắng/thua đang bất định, và giảm regret nếu định nghĩa được chính sách lựa chọn sau câu trả lời. Hiển thị ví dụ hai đáp án dẫn tới hai shortlist/khuyến nghị khác nhau.

Nếu không có phân phối xác suất câu trả lời, không gọi chỉ số này là expected information gain hoặc expected value of information. Có thể dùng chỉ số bảo thủ theo nhánh xấu nhất, nhưng phải định nghĩa và kiểm chứng riêng. Độ rộng khoảng điểm giảm là chỉ số phụ; nó có thể không làm thay đổi quyết định.

## 7. Những điểm phải chỉnh trong hợp đồng đầu vào

1. **Tách `Không cần` và `Chưa biết`.** Có thể giữ bốn mức ưu tiên `Bắt buộc/Quan trọng/Nên có/Không cần`, thêm một trạng thái chưa biết/để trống. Không cần nghĩa là bỏ mục tiêu khỏi đánh giá; chưa biết nghĩa là chưa xác định sở thích và cần phân tích kịch bản.
2. Phân biệt chưa biết giá trị môi trường với chưa biết mức ưu tiên; hai loại tạo miền kịch bản khác nhau.
3. Hiện trạng như đang chạy AWS hoặc có hợp đồng Databricks chưa tự là HARD. Mapping cần giải thích vì sao nó thành ràng buộc hoặc ưu tiên.
4. Không suy benchmark, SLA hoặc sức chịu tải chỉ từ số bảng và số engine ghi.
5. Hai mục dễ vận hành/tránh lock-in có thể nằm trong schema mở rộng, nhưng chưa bật thành tiêu chí mặc định hoặc tự sửa input v1. Cần định nghĩa đại lượng/rubric khi đưa vào thử nghiệm.

Những thay đổi này là đề xuất trước triển khai; không ghi là người dùng đã xác nhận lại form.

## 8. Kiểm chứng nên dùng công nghệ gì

**pytest cho ca cụ thể, Hypothesis cho thuộc tính.** Hypothesis sinh input và tìm phản ví dụ, tích hợp được với pytest. Việc sinh nhiều input chỉ có ý nghĩa khi thuộc tính/oracle độc lập với công thức đang kiểm tra. [Hypothesis Quickstart](https://hypothesis.readthedocs.io/en/latest/quickstart.html)

Các kiểm tra có giá trị trực tiếp:

- Không scope bị FAIL HARD nào được gắn đủ điều kiện.
- Không ghép hai scope hoặc hai điều kiện loại trừ để tạo PASS giả.
- Trong cùng miền kịch bản và chính sách giá trị, thêm HARD không làm xuất hiện phương án khả thi mới.
- Tăng giá trị một tiêu chí với trọng số cố định không làm điểm của chính ứng viên giảm.
- Hoán vị catalog, claim hoặc câu hỏi không đổi kết quả ngữ nghĩa.
- Bổ sung thông tin nhất quán thu hẹp miền: tính khả thi phản ánh đúng miền con; với tập khả thi của ứng viên không đổi, khoảng điểm không mở rộng.
- Tập nới được trả ra thực sự có nghiệm theo loại bảo đảm đã công bố và giữ mọi điều kiện được bảo vệ.
- Mọi lý do có rule/requirement/claim ID; không có bằng chứng thì không tự sinh câu khẳng định hỗ trợ.
- Chạy lại snapshot bằng cùng phiên bản engine thu được cùng kết quả, kể cả tie và làm tròn.

Đối chứng đề xuất: (A) chỉ lọc HARD; (B) lọc HARD rồi Weighted Sum trên đầu vào đầy đủ/preset có nhãn; (C) mô hình đề xuất có xử lý thiếu input, giải thích và chẩn đoán. Đánh giá riêng giá trị từng chức năng, không chỉ xem có đổi top-1 hay không.

Tách fixture tổng hợp để kiểm tra logic khỏi tình huống catalog thực. Chia tình huống hiệu chỉnh/kiểm tra trước khi sửa trọng số; các biến thể gần giống nhau của một tình huống không nên rơi vào hai tập. Chuyên gia có thể chấm shortlist, lý do và điều kiện làm mù tên phương pháp; giữ lại bất đồng, không coi một catalog là ground truth duy nhất.

## 9. Thư viện/cơ chế đã xem nhưng chưa nên đưa vào lõi

| Công nghệ | Đánh giá cho v1 | Khi xem lại |
|---|---|---|
| Z3 | Có ích về tính nhất quán và chẩn đoán nhưng chưa cần cho bộ hữu hạn nhỏ | Đo được vấn đề tổ hợp hoặc yêu cầu quan hệ phức tạp |
| pyDecision | Có WSM và nhiều phương pháp MCDA; công thức tổng hợp chưa phải phần khó nhất của hệ này | Cần đối chiếu phương pháp trên cùng ma trận giá trị đã kiểm soát |
| NumPy | Tùy chọn tối ưu bảng điểm sau profiling | Python thuần thực sự là nút thắt |
| Neo4j/OWL | Chưa có truy vấn/suy diễn quan hệ bắt buộc mà JSON không phục vụ được | Xuất hiện nhu cầu ontology hoặc khai thác quan hệ rõ ràng |
| RAG/vector DB/LangChain | Chưa phục vụ nhu cầu form xác định hiện tại | Mở phạm vi sang tìm kiếm hoặc hỏi đáp tài liệu |
| LLM | Chưa cần cho chọn, chấm hoặc giải thích từ template | Cần diễn đạt lại trace và đã có kiểm tra độ bám dữ liệu |
| Redis/Celery/Kubernetes | Chưa có tải đo được đòi hỏi | Có tác vụ dài, nhiều phiên đồng thời hoặc vận hành nhiều instance |

Khả năng WSM và các họ MCDA của pyDecision được ghi trong repository chính thức. Điều đó không cung cấp sẵn mapping từ form, scope matching hoặc semantics thiếu dữ liệu riêng của đề tài. [pyDecision](https://github.com/Valdecy/pyDecision)

Không cần chạy Spark, Trino hay các catalog thật để chứng minh logic MVP theo giả định hiện tại. Lab tích hợp là bước tạo bằng chứng kỹ thuật khác, có thể nối thêm sau; không phải dependency runtime của ứng dụng khuyến nghị.

## 10. Thứ tự triển khai và điều kiện hoàn thành

| Mốc | Sản phẩm cụ thể | Điều kiện qua mốc |
|---|---|---|
| 1. Hợp đồng và dữ liệu nhỏ | Schema + một lát cắt ba catalog được chọn rõ + fixture tổng hợp | Mọi ô đang dùng có kiểu, scope, trạng thái unknown và nguồn hoặc nhãn giả định |
| 2. Lõi đầu vào đầy đủ | Normalize, joint gate, Weighted Sum, trace | Có ca PASS/FAIL/tie và đối chiếu tính tay độc lập |
| 3. Thiếu input | Scenario generator, khoảng, thống kê thắng và regret | Không có kịch bản bất khả thi; tính exact có giới hạn được công bố |
| 4. Chẩn đoán | Conflict, tập nới, danh sách thông tin đáng làm rõ | Tập nới được kiểm lại; có ví dụ câu trả lời thực sự đổi quyết định |
| 5. Giao diện | Form, nhóm ứng viên, khoảng điểm, lý do mở rộng, export JSON | Một luồng submit đến kết quả chạy qua đúng cùng engine đã test |
| 6. Kiểm chứng đề tài | Tập kiểm tra giữ riêng, báo cáo lỗi/độ nhạy/đối chứng | Báo được cả ca không phân biệt và thất bại; chưa suy ra đúng thực tế từ logic đúng |

Mốc 1–2 nên chạy được trước khi dành nhiều công cho UI. Không gắn thời hạn chắc chắn khi chưa biết kỹ năng Python/React, thời gian và mức hoàn thiện KB.

Giao diện tối thiểu gồm form, màn kết quả và phần mở rộng lý do. Khoảng điểm nên vẽ bằng thanh ngang min–max chung thang giá trị, đặt nhãn tính khả thi ngay bên cạnh. Không buộc biểu đồ hoặc thứ hạng tổng khi các ứng viên chưa so sánh chắc chắn được.

Điều kiện hoàn thành MVP: cùng một ca có thể đi từ form tới kết quả truy vết được, xử lý thiếu input có semantics rõ, chỉ ra được một sửa chữa hợp lệ và một thông tin có ảnh hưởng, tái lập được bằng snapshot, và vượt qua các kiểm tra logic có oracle. Kết quả đó chứng minh ứng dụng thực hiện mô hình đã công bố; chất lượng khuyến nghị thực tế còn phụ thuộc dữ liệu và kiểm chứng miền.
