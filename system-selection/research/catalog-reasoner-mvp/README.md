# MVP chọn catalog lakehouse — 7 ứng viên

**Cập nhật 18/10/2026:** giao diện mặc định dùng form v3, có storage, thao tác theo engine, local lab và số bảng chính xác tùy chọn. Đánh giá một cấu hình có bằng chứng tương thích cho từng catalog; vẫn giữ API v2 để đối chiếu. Python chỉ dùng standard library, hàm suy luận thuần, không LLM hoặc network.

[Bản nâng chất lượng và hai bài thực nghiệm](experiments/quality-upgrade-2026-10-18/README.md), [đặc tả input v3](../catalog-knowledge-base/input-v3.md), [tri thức bổ sung](../catalog-knowledge-base/evidence-review-2026-10-18.md). Hai ca nguồn hiện có một phương án documented fit mỗi ca; những ca thiếu storage, capacity hoặc đường triển khai vẫn conditional. KB gốc/trọng số giữ nguyên; tri thức mới được merge từ overlay có phiên bản. Cùng input, KB, config và seed cho cùng kết quả.

Các phần v2 dưới đây được giữ để mô tả hợp đồng và báo cáo lịch sử 17/10. Với v3, candidate bindings đã có resolver dùng profile nguyên vẹn. Scenario chỉ so sánh các profile có bằng chứng và context được xác định; chưa đủ cơ sở so sánh thì metrics null, không bịa tỷ lệ thắng. `quality-policy.json` ghi các giả định mới; nguyên config trọng số không đổi.

Kiểm chứng hiện tại là **logic/hợp đồng phần mềm**. Đọc [báo cáo cuối](outputs/mvp/final-report.md) và [giới hạn một trang](outputs/mvp/limitations.md) trước khi diễn giải kết quả trên KB thật.

## Chạy

Từ thư mục này:

```powershell
python -m catalog_reasoner.project_io --answers ../../sites/catalog-review/artifacts/group1-payload.json --output outputs/my-result.json
python -m pytest
python -m catalog_reasoner.evaluation
```

Không chỉ định `--answers` thì đọc stdin. Hàm chính: `run_case(form_answers, kb, config)` trong [application.py](catalog_reasoner/application.py). Nạp file bằng `load_project_config()` và `load_kb()` tại [project_io.py](catalog_reasoner/project_io.py); không I/O trong `run_case`.

Giao diện: chạy `node server.mjs` từ `system-selection/sites/catalog-review`, mở `http://127.0.0.1:4317`. Đặt `CATALOG_PYTHON` nếu cần Python riêng. Payload đi qua stdin của tiến trình cố định, không ghép shell; có giới hạn kích thước, timeout và concurrency từ config. Chưa có deploy public/xác thực trong MVP.

## Suy luận

1. Chuẩn hóa form bằng registry. `needs_input_correction` trả lỗi có đường dẫn trường và chặn suy luận.
2. Dịch bằng [bảng tường minh](../catalog-knowledge-base/layer-2-kb-values.json), không đổi KB/tự đoán alias. Chỗ thiếu giữ unknown.
3. Validate property/qualifier/rubric; tra đúng scope và qualifier. Quantity chỉ so quota đã biết, đúng boundary và điều kiện.
4. Lọc HARD thành ba nhóm. Thiếu thông tin form giữ conditional, kể cả khi thử nới HARD.
5. Weighted Sum SOFT trên thang tuyệt đối; thiếu weight dùng config và gắn cờ. Không SOFT thì không tạo điểm hoặc người thắng.
6. Duyệt hết miền hữu hạn hoặc lấy mẫu có seed. Tổng đánh giá completion, gồm cặp phản thực để đo ảnh hưởng, không vượt max_scenarios. Đồng hạng chia đều credit. Format/storage chưa biết được chia sẻ; các cell KB thiếu được điền độc lập theo rubric.

Tỷ lệ kịch bản dựa trên phân phối giả định, không phải xác suất phù hợp thực tế. Sampling trả `max_regret_observed` và cận trên bảo thủ; không gọi giá trị quan sát là cực đại toàn cục. Candidate bindings chỉ là trace, không có joint path resolver.

## Cấu hình và bằng chứng

- [config.json](config.json): 0/0,5/1, high/low 3/1, max_scenarios 500, seed 42; giữ nguyên file gốc.
- [config Lớp 2](../catalog-knowledge-base/layer-2-runtime-config.json): HARD mặc định, 7 scope, khoảng số bảng.
- [mvp-settings.json](mvp-settings.json): đồng hạng/regret, ngân sách sampling/ảnh hưởng, ±30%/1.000 lần và transport; có nhãn assumption.

Output ghi config, assumptions, profile, revision, requirement và claim ID. Ghi chú “reserved” trong config gốc là lịch sử mốc bước 1–2; runtime hiện dùng các tham số đó ở bước 3–4.

Tập [hiệu chỉnh 6 ca](cases/calibration.json) và [kiểm tra 4 ca](cases/holdout.json) khóa bằng [hash](cases/split-manifest.json) trước khi triển khai phần còn lại. Hồ sơ tổng hợp; dữ liệu ứng viên lấy từ KB thật. Không dùng holdout để chỉnh KB/trọng số hoặc tối ưu kết quả. Lỗi cấu trúc được tái hiện bằng unit test tổng hợp riêng.

[Kết quả từng hồ sơ](outputs/mvp/summary.json), [CSV](outputs/mvp/summary.csv), [độ nhạy](outputs/mvp/weight-sensitivity-calibration.json), [51 phép đổi đáp án](outputs/mvp/form-perturbations.json), [phiếu chuyên gia](outputs/mvp/expert-score-sheet.html). Độ nhạy chỉ áp dụng ca hiệu chỉnh hợp lệ có SOFT; ca khác ghi rõ không áp dụng. Chưa có đánh giá chuyên gia.

`python -m catalog_reasoner --kb ... --requirements ... --config ...` và output `synthetic-stage12-*` là đường kiểm thử lịch sử, không phải tích hợp form hiện hành. Fixture [synthetic-mvp-case.json](examples/synthetic-mvp-case.json) có 3 ứng viên tổng hợp, 6 yêu cầu, đi qua suy luận/validator hiện hành để kiểm tra ba trạng thái UI.
