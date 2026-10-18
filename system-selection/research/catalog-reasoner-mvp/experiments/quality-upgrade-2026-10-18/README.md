# Nâng chất lượng suy luận cho bài toán có nguồn công khai

Ngày 18/10/2026. **Hai ca nguồn đã tìm được đường triển khai có bằng chứng đáp ứng các yêu cầu đã khai báo.** Hệ thống giữ rõ những ứng viên chưa đủ bằng chứng và các điều kiện cấu hình cần thực hiện. Đây là đánh giá tính phù hợp của thiết kế theo tài liệu, chưa phải chứng nhận một hạ tầng đang hoạt động.

## Những gì đã sửa

1. **Không mất storage và thao tác.** Form v3 có storage cụ thể, thao tác theo từng engine và số bảng chính xác nếu biết. Spark đọc không tự chứng minh Spark ghi. AWS không tự thành S3. Lab cục bộ có đáp án riêng, không đồng nhất với on-prem sản xuất. Form v2 vẫn được hỗ trợ nguyên hợp đồng cũ.
2. **Chọn một cấu hình triển khai nguyên vẹn.** API/connector là lựa chọn thiết kế mà hệ thống đề xuất bằng chứng; storage/môi trường/thao tác là dữ kiện đầu vào. Không ghép claim tốt nhất từ các cấu hình không tương thích. Output có profile, bindings, nguồn, điều kiện phiên bản và yêu cầu cấu hình.
3. **Bổ sung tri thức có provenance.** Thêm 15 claim qua một lớp dữ liệu phiên bản riêng và hai profile tương thích. Không ghi đè KB gốc hoặc sửa trọng số. Claim vẫn được phân biệt với việc đã triển khai/được chuyên gia độc lập duyệt.
4. **Số bảng vẫn là HARD.** Nếu chỉ chọn `<100`, vẫn phải xét toàn khoảng tới 99. Số chính xác chỉ thu hẹp nhu cầu khi người dùng khai báo hợp lệ. Một ví dụ nguồn có thể chứng minh cận dưới số bảng trong recipe; không biến nó thành quota tối đa hay chứng cứ hiệu năng.
5. **Không tính tỷ lệ thắng từ đường ghép giả.** Ứng viên chưa có cấu hình nguyên vẹn được xác minh vẫn conditional, có khoảng SOFT nếu áp dụng, nhưng không được điền API độc lập để tạo tỷ lệ khả thi/thắng. Chưa đủ ứng viên có thể so sánh thì metrics để null và nói rõ lý do. Ngưỡng và phạm vi so sánh ghi trong `quality-policy.json`, có nhãn assumption và được echo ở đầu ra.

## Hai bài thực nghiệm

| Bài toán | Dữ kiện thêm vào form v3 | Kết quả thực thi |
|---|---|---|
| Phân quyền phân tích Iceberg trên AWS | S3; Spark đọc, append, CREATE TABLE thường; lab giới hạn đúng 5 bảng | **Glue + EMR Serverless + Lake Formation: eligible** trong recipe đã ghi; sáu ứng viên còn conditional |
| Thay đổi ETL trên nhánh catalog rồi công bố | Local lab; filesystem cục bộ; Spark đọc, append, CREATE TABLE; một bảng | **Nessie native SparkCatalog: eligible** trong recipe đã ghi; sáu ứng viên còn conditional |

Nguồn: [worked example AWS](https://aws.amazon.com/blogs/big-data/fine-grained-access-control-in-amazon-emr-serverless-with-aws-lake-formation/), [EMR FGAC](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/emr-serverless-lf-enable.html), [walkthrough Nessie](https://www.dremio.com/open-source/nessie/), [Nessie Spark chính thức](https://projectnessie.org/iceberg/spark/), [catalog transactions](https://projectnessie.org/guides/transactions/).

Hai hồ sơ là **lab tổng hợp dựa trên nguồn**, không phải tổng quy mô doanh nghiệp gốc. Nhu cầu chính xác 5/1 bảng là phạm vi lab được công khai trong [evaluation-config.json](evaluation-config.json). Ngay cả khi có nguồn, im lặng về một nhu cầu không được diễn giải thành không cần.

Đây không phải phép so sánh hai phiên bản trên input đồng nhất: bản mới chuyển thêm các dữ kiện vốn có trong bài vào form, sửa phân loại local lab và khai báo rõ số bảng thực nghiệm. Payload v2 cũ không tự được bổ sung những thông tin ấy. Những kết quả cũ vẫn được giữ ở thư mục thực nghiệm ngày 17/10.

Payload và kết quả có thể xem trực tiếp:

- AWS: [form](forms/SOURCE-V3-AWS.json), [requirements](results/SOURCE-V3-AWS.requirements.json), [toàn bộ trace](results/SOURCE-V3-AWS.json).
- Nessie: [form](forms/SOURCE-V3-NESSIE.json), [requirements](results/SOURCE-V3-NESSIE.requirements.json), [toàn bộ trace](results/SOURCE-V3-NESSIE.json).
- [CSV tổng hợp](results/summary.csv), [JSON tổng hợp](results/summary.json), [manifest kiểm chứng/config/hash](results/verification.json).

## Ca biên và phản thực đã chạy

| Thay đổi so với ca nguồn | Hành vi quan sát |
|---|---|
| Bỏ số chính xác, chỉ giữ bucket `<100` | Nessie còn conditional do capacity; đường chức năng vẫn có bằng chứng |
| Storage AWS = chưa biết | Conditional; không suy S3 từ cloud |
| Thêm MERGE chưa có đường được rà soát trong danh mục | Conditional; không gọi là không hỗ trợ |
| Đổi local lab thành on-prem sản xuất | Conditional; recipe lab không tự chứng minh production |
| Thao tác của Spark chưa rõ | Conditional; không tự mặc định chỉ đọc |
| Nhiều loại engine writer | Conditional khi chưa chứng minh concurrency đúng đường |
| Số bảng chính xác mâu thuẫn với bucket | Input error, không chạy suy luận |
| Branching đổi thành nice-to-have | Có SOFT và khoảng điểm Nessie [1, 1]; không bịa tỷ lệ thắng khi chưa đủ cấu hình xác minh để so sánh |

Các ca này được đặt tên `SYNTHETIC-…`. Chúng kiểm tra hành vi và ranh giới bằng chứng, không phải bài toán doanh nghiệp độc lập. Ca nguồn là dữ liệu phát triển đã dùng để cải thiện hệ thống, không phải holdout mới. Bộ calibration/holdout cũ và hash của chúng giữ nguyên.

## Đưa một bài trên mạng vào hệ thống từ nay

1. Lưu URL, ngày đọc và phần nguồn chứa yêu cầu. Dùng [mẫu hồ sơ có provenance](public-problem-template.json).
2. Tách dữ kiện nguồn, suy luận có căn cứ, lựa chọn lab và thông tin chưa biết. Nếu bài chỉ nói Spark thì phải xem nó đọc/append/MERGE gì; không suy thêm engine vì tên bên đăng bài.
3. Điền form v3 theo đúng phạm vi. Nếu nguồn chỉ có ví dụ nhỏ thì gọi đó là lab nhỏ; không gán thành quy mô sản xuất. Các API nội bộ do hệ thống chọn, người ra quyết định không cần tự chọn.
4. Chạy cùng `run_case`. Khi có đủ bằng chứng, hệ thống chỉ ra cấu hình có thể đáp ứng; khi thiếu, xem requirement/claim và câu hỏi còn thiếu. Candidate không có chứng cứ chưa được coi là bị loại.
5. Nếu thiếu tri thức, bổ sung claim có scope, qualifier, nguồn và giới hạn; khi kết hợp nhiều thành phần phải bổ sung profile có chứng cứ tương thích. Không thêm alias hoặc `none` chỉ để ra một người thắng.
6. Lưu kết quả trước khi chỉnh tiếp. Muốn đánh giá chất lượng khuyến nghị, cần thêm hồ sơ độc lập và người thẩm định; hai ca phát triển này không đủ để tính accuracy.

**Hiện chưa có tính năng tự đọc mọi URL và tự xác nhận yêu cầu đúng.** Phần chuẩn bị hồ sơ nguồn vẫn cần đối chiếu; lõi tính toán không dùng LLM/network và cho cùng kết quả khi input, tri thức, config, seed không đổi. Đây là giới hạn rõ ràng của chức năng hiện có.

## Bằng chứng kiểm chứng và chạy lại

Chạy từ thư mục gốc dự án:

```powershell
& 'C:/Users/Admin/miniconda3/python.exe' 'system-selection/research/catalog-reasoner-mvp/experiments/quality-upgrade-2026-10-18/run_evaluation.py'
```

Các kiểm thử gốc vẫn có và thêm test intake, overlay, resolver, scenario không ghép profile. Báo cáo kiểm thử và coverage nằm tại `../../outputs/quality-upgrade-tests.xml` và `../../outputs/quality-upgrade-coverage.json`. Kiểm tra UI thực đi qua Python backend, bao gồm payload, profile/claim, lỗi trường, focus và màn 375px; artifact nằm tại `../../../../sites/catalog-review/artifacts/e2e-v3.json`.

Kết quả kiểm tra cuối: **241 test Python qua, 30 test JavaScript/API qua; coverage Python 92,69%** theo phép đo gồm pytest và chạy thực nghiệm. Mười hồ sơ kiểm tra đều có hành vi mong đợi; browser E2E không có page error hoặc tràn ngang ở 375px. [Báo cáo kiểm chứng tổng hợp](../../outputs/quality-upgrade-final-verification.json). Các số liệu này kiểm chứng phần mềm và các ca đã nêu, không chứng minh accuracy khuyến nghị ngoài thực tế.

Bản chạy trong phiên hiện tại: [mở form v3](http://127.0.0.1:52831/#form). Đây là server localhost của phiên làm việc, không phải website đã triển khai public; có thể chạy lại `node server.mjs` trong `system-selection/sites/catalog-review` nếu phiên server đã kết thúc.

## Điều vẫn phải giới hạn khi viết báo cáo

`eligible` ở đây nghĩa là có thiết kế được tài liệu chứng minh trong phạm vi cụ thể, với prerequisites được liệt kê. Chưa chạy lại Spark/AWS/Docker, chưa đo throughput, độ trễ, chi phí hay production readiness. Cận dưới số bảng không chứng minh quota tài khoản hiện tại hoặc headroom trên một catalog đã chứa dữ liệu khác.

Danh mục profile hiện có hai đường được rà soát; giữ cả bảy ứng viên nhưng sáu ứng viên chưa đủ chứng cứ trong mỗi ca không có nghĩa chúng kém hơn. Không có nhãn catalog tối ưu duy nhất từ bài nguồn. Bộ Spark/Scala/Iceberg/Nessie cần khớp phiên bản; recipe AWS giữ phân biệt quyền SELECT và quyền ghi IAM, không cam kết CTAS hoặc mọi DML.
