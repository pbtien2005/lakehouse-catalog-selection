# Báo cáo hoàn thiện MVP catalog lakehouse

Ngày 17/10/2026. **Phần mềm đã nối và chạy đầu-cuối với cả 7 scope thật. Chưa có cơ sở để gọi khuyến nghị là đúng thực tế.** KB và config/trọng số suy luận gốc không đổi. Người dùng đã cho phép đi tiếp toàn bộ các mốc và đã duyệt riêng bản vá tràn màn hình.

## Trạng thái theo sáu giai đoạn đã yêu cầu

| Giai đoạn | Trạng thái | Phát hiện chính | Việc cần người dùng quyết |
|---|---|---|---|
| 1. Nhất quán các lớp | qua | Registry 10 câu/48 đáp án; UI có 9 câu vì I06 bất hoạt. 12 property đích tồn tại; 25 property còn lại giữ nguyên. 33 dòng quy đổi tường minh, 17 dòng thiếu miền giá trị. | Chưa cần đổi form; xem tác động thực tế của I04/I09 bên dưới |
| 2. Nối đầu-cuối | qua | `run_case` nối Lớp 2, validator, bốn bước Lớp 3. Chạy ba hồ sơ viết tay và lưu đầy đủ trace. Input lỗi chặn suy luận. | Không còn quyết định triển khai kỹ thuật |
| 3. Giao diện | qua | Ba hồ sơ thật khớp payload/nhóm/điểm/trace; thêm ca tổng hợp từ Python xác minh ba nhóm đều có phần tử. Bàn phím có focus, màn 375px không tràn sau bản vá đã duyệt. | Không cần duyệt lại thiết kế |
| 4. Bộ hồ sơ tình huống | lỗi | Đã khóa/chạy 6 hiệu chỉnh + 4 kiểm tra. Đạt 3/4 hành vi; chưa có ứng viên thật bị loại chắc chắn. Cả 9 ca hợp lệ đều 7 conditional, 0 eligible, 0 excluded. Một ca mâu thuẫn bị chặn. | Cần quyết định vòng bổ sung/kiểm chứng KB và chính sách xác nhận path nếu muốn kết luận chắc chắn |
| 5. Kiểm chứng tối thiểu | qua | Năm tính chất logic qua; độ nhạy ±30%, 1.000 lượt cho mỗi ca hiệu chỉnh có SOFT; hai đối chứng và bảng theo hồ sơ đã xuất. Phiếu chuyên gia đã chuẩn bị, chưa đánh giá thay con người. | Chọn người kiểm chứng KB/chuyên gia trước khi sử dụng thực tế |
| 6. Tài liệu giới hạn | qua | Có bản giới hạn, toàn bộ config/assumptions trong output, giới hạn sampling/regret và phần hoãn | Chưa cần thêm thuật toán/trọng số |

“Lỗi” ở giai đoạn 4 là thiếu độ phủ hành vi trên dữ liệu thật; không được sửa KB hoặc diễn giải missing thành none để làm test đẹp. Thuật toán tạo được eligible/conditional/excluded trên fixture tổng hợp có chứng cứ rõ, qua cùng validator/suy luận.

## Bằng chứng chạy

- **164 test Python qua**, không lỗi/skip: [JUnit](../mvp-tests.xml), [coverage](../mvp-coverage.json). Coverage tổng được công cụ đo và ghi trong [verification.json](verification.json); có tính cả lần thực thi evaluation. Đây không phải chứng minh đầy đủ mọi tình huống.
- **26 test JavaScript/API qua**: [log](../../../../sites/catalog-review/artifacts/mvp-js-tests.log), [JUnit](../../../../sites/catalog-review/artifacts/mvp-js-tests.xml). Coverage core.js 100% dòng, 97,22% nhánh; không coi đó là coverage toàn bộ UI/server.
- **74 kiểm tra Lớp 2 qua**, gồm thực thi 48 đáp án, kiểm tra từ điển/anchor và hash: [layer-2-validation.json](../../../catalog-knowledge-base/layer-2-validation.json).
- [E2E trình duyệt](../../../../sites/catalog-review/artifacts/e2e-mvp.json): ba hồ sơ thật, một kết quả tổng hợp từ backend có đủ ba nhóm, lỗi none/rank, khớp trace và payload, keyboard/focus, màn hình hẹp; không page error.
- PDF chuyên gia đã xác minh **10 trang, đúng một hồ sơ/trang**, kiểm tra text và render bằng PDFium/Poppler. Không kèm xếp hạng hoặc kết quả hệ thống: [PDF](../../output/pdf/expert-score-sheet.pdf), [HTML](expert-score-sheet.html).
- `npm audit --offline` không báo lỗ hổng trên graph không có package runtime bên ngoài. Runtime quyết định dùng Python stdlib, server dùng Node built-ins; đây không là kiểm toán toàn bộ máy hoặc toolchain.

Lỗi được tái hiện trước khi sửa và test lại, gồm: tham chiếu registry, readiness, boundary malformed, quota, bỏ sót input chưa rõ trong chẩn đoán nới, biến completion thừa và ngân sách counterfactual. Tổng đánh giá completion không vượt 500; các phép so sánh ảnh hưởng dùng cùng ngân sách/cache.

## Đầu ra và giới hạn quan trọng

HARD có ba trạng thái; unknown không tự thành đạt/loại. SOFT dùng Weighted Sum tuyệt đối và khoảng điểm; không SOFT thì trả null thay vì bịa điểm/người thắng. Tỷ lệ đứng đầu là tỷ lệ kịch bản giả định, đồng hạng chia đều credit. Kịch bản không ai đáp ứng HARD được ghi riêng; tỷ lệ đứng đầu các ứng viên do đó không nhất thiết cộng thành 100%.

Khi lấy mẫu, regret là **cực đại quan sát**, kèm cận trên bảo thủ và cờ không phải cực đại đã được chứng minh. Unknown được xếp theo thay đổi người đứng đầu khi can thiệp một biến, giữ các biến khác cố định; biến không đủ ngân sách đo có null, không giả là ảnh hưởng bằng không.

Candidate bindings vẫn chỉ trace. API/path mở còn một trường hợp chưa có bằng chứng, nên không thể đóng miền chỉ từ các API đã quan sát. Khả thi trong kịch bản chỉ là đáp ứng mức HARD đã điền, chưa chứng minh các path tương thích cùng nhau. Thêm claim đơn thuần chưa tự giải quyết hết giới hạn này.

## Kết quả theo hồ sơ

[CSV đầy đủ](summary.csv), [JSON tổng hợp/đối chứng](summary.json), [JSON từng hồ sơ](results/SYNTHETIC-C01.json). Mỗi file trong thư mục `results` có assumptions/config và trace đầy đủ.

| Hồ sơ tổng hợp | Tập | Eligible / Conditional / Excluded | Đứng đầu kịch bản theo seed hiện tại |
|---|---|---|---|
| C01 — AWS/Spark/Iceberg cơ bản | hiệu chỉnh | 0 / 7 / 0 | Không có SOFT |
| C02 — branching/federation nice-to-have | hiệu chỉnh | 0 / 7 / 0 | AWS Glue |
| C03 — Databricks/Delta/quyền chi tiết | hiệu chỉnh | 0 / 7 / 0 | Không có SOFT |
| C04 — nhiều writer, atomic bắt buộc | hiệu chỉnh | 0 / 7 / 0 | AWS Glue |
| C05 — nhiều thông tin chưa biết | hiệu chỉnh | 0 / 7 / 0 | Không có SOFT |
| C06 — none mâu thuẫn và thiếu rank | hiệu chỉnh | Chặn input | Không suy luận |
| T01 — GCP/Trino/nhánh bắt buộc | kiểm tra | 0 / 7 / 0 | Không có SOFT |
| T02 — on-prem/Hudi/quy mô lớn | kiểm tra | 0 / 7 / 0 | Không có SOFT |
| T03 — đa cloud/hỗn hợp/nhiều yêu cầu | kiểm tra | 0 / 7 / 0 | Không có SOFT |
| T04 — AWS-native/DuckDB/two nice-to-have | kiểm tra | 0 / 7 / 0 | Unity Catalog Databricks |

Đứng đầu kịch bản ở bảng này **không phải khuyến nghị triển khai**. Không hồ sơ nào có người thắng eligible chắc chắn; các khoảng SOFT còn chồng lấn. Thứ tự có thể chịu ảnh hưởng giả định điền cell thiếu và lấy mẫu, không chỉ bằng chứng đã xác lập.

Ba hồ sơ viết tay: [ca dễ](written-easy-full-trace.json), [nhiều unknown](written-many-unknown-full-trace.json), [không eligible](written-no-eligible-full-trace.json). Chẩn đoán nới luôn giữ yêu cầu chưa biết; không hứa bỏ một HARD sẽ giải quyết mọi điều kiện.

## Độ nhạy và đối chứng

[Độ nhạy trên tập hiệu chỉnh](weight-sensitivity-calibration.json): C02 và C04 có SOFT nên mỗi ca chạy 1.000 lượt, thay một weight trong ±30%, seed 42, dùng cùng completion scenarios. C01/C03/C05 không SOFT nên không áp dụng; C06 lỗi input nên không áp dụng. Với một SOFT như C04, thay weight không đổi Weighted Sum đã chuẩn hóa — đây là tính chất của công thức, không là bằng chứng mô hình mạnh.

Đối chứng nền tảng chỉ ánh xạ Databricks → Unity Catalog Databricks, AWS-native → Glue; Snowflake không có ứng viên tương ứng nên không bịa lựa chọn. Đối chứng đếm chỉ đếm yêu cầu full đã xác lập, không cộng unknown. Khác biệt từng hồ sơ nằm trong summary JSON/CSV. T04: đối chứng nền tảng chọn Glue, hệ thống đứng đầu kịch bản là Unity Catalog Databricks. C02: đối chứng đếm đồng hạng cả bảy, hệ thống có Glue đứng đầu kịch bản. Không có SOFT thì hệ thống không chọn người thắng; so sánh khác biệt kiểu này cần được đọc đúng, không coi là hệ thống sai hoặc tốt hơn đối chứng.

## Phép đổi đáp án qua đường chính thức

[51 lượt kiểm tra](form-perturbations.json) gồm toàn bộ 48 ID và cả hai rank cho ba nhu cầu I10. So sánh nhóm/điểm/metrics, không lấy việc raw payload/trace thay đổi làm bằng chứng quyết định thay đổi; thay đổi chứng cứ được ghi riêng.

- I01/I02/I03/I05/I07/I08/I10 có ít nhất một đáp án làm đổi đầu ra quyết định trên hồ sơ nền đã ghi.
- I04 chưa làm đổi quyết định hoặc mức chứng cứ vì không có quota đủ điều kiện đúng boundary catalog.
- I09 không đổi quyết định đúng theo chính sách chỉ giữ bối cảnh.
- I06 không đổi vì đang bất hoạt; không gửi từ UI.

Đây là kiểm tra trên một hồ sơ nền xác định, không chứng minh ảnh hưởng phổ quát. Không tự bỏ I04/I09 hoặc mở I06 sau kết quả này.

## Lệch phạm vi đã xử lý và phần không đổi

Gỡ operations/portability/storage/tên hồ sơ/priorities năm bậc khỏi payload; bỏ evaluator JavaScript và fixture sản phẩm giả. Dùng registry chung; không thêm câu authentication, vận hành hoặc lock-in. Dùng đủ bảy scope do người dùng chọn. Giữ nguyên KB, 37 property, property-plan và config/trọng số suy luận gốc. Riêng CSS đã áp dụng đúng bản vá tràn được người dùng duyệt; hash trước/sau được ghi trong verification.

## Việc cần quyết và đề xuất sau MVP

Không còn quyết định chặn phần mềm MVP. Nếu muốn dùng cho khuyến nghị thực tế, cần chốt hai việc ở [kế hoạch dữ liệu/path](kb-next-actions.md): **kiểm chứng/bổ sung KB** và **cách xác nhận API/path hoặc miền được phép**. Đề xuất ưu tiên kiểm chứng dữ liệu và xác nhận thủ công các đường quan trọng; chưa mở scope tự động joint path resolution.

Đề xuất sau MVP tách riêng: expert review; bổ sung bằng chứng cho các hợp đồng thiếu; xem lại I04 sau khi có quota; chỉ xem xét streaming/tiêu chí mới hoặc deploy public khi có yêu cầu riêng. Chưa tự thực hiện các thay đổi đó.

[Giới hạn một trang](limitations.md) · [bảng ánh xạ và nguồn lý do](domain-mapping-review.md) · [hướng dẫn chạy](../../README.md).
