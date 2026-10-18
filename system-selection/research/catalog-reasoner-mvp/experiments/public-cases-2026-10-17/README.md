# Hai bài toán công khai để thực nghiệm hệ thống chọn catalog

Ngày nghiên cứu: **17/10/2026**. Đã chuyển thành payload của form hiện tại và chạy thật qua `run_case` của dự án với cả bảy ứng viên. **Chỉ chạy hệ thống chọn catalog; chưa triển khai lại hạ tầng lakehouse của các bài hướng dẫn.**

Hai hồ sơ là **lab tổng hợp dựa trên nguồn công khai**, có lựa chọn giới hạn phạm vi được ghi rõ. Chúng có đủ dữ liệu để thử luồng ánh xạ, suy luận và giải thích; không phải hai bộ yêu cầu doanh nghiệp đã được khảo sát đầy đủ. Chi tiết từng đáp án và căn cứ nằm trong [casebook.json](casebook.json); mọi tham số lab nằm trong [experiment-config.json](experiment-config.json).

## Bài toán 1 — Phân quyền phân tích tài chính trên AWS

**Cần giải quyết:** chia sẻ bảng Iceberg cho nhóm phân tích, đồng thời giới hạn cột nhạy cảm và những hàng được phép đọc. Phương án tham chiếu trong nguồn kết hợp Glue, Lake Formation và Spark trên EMR Serverless, kèm notebook nạp dữ liệu/kiểm tra quyền. [Hướng dẫn AWS](https://aws.amazon.com/blogs/big-data/fine-grained-access-control-in-amazon-emr-serverless-with-aws-lake-formation/).

**Thiết kế lab:** giữ đường Spark, chọn tập bảng tài chính có tên trong nguồn và giữ cơ chế credential tạm thời cho truy cập dữ liệu đã đăng ký. Cơ chế cấp credential được mô tả trong [tài liệu EMR Serverless](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/emr-serverless-lf-enable.html). Phạm vi tập bảng và việc giữ nền tảng AWS là quyết định của lab, không phải thông tin về hợp đồng hoặc quy mô sản xuất của tác giả.

**Vì sao phù hợp:** kiểm tra được hai nhánh yêu cầu bảo mật của form cùng một lúc; đồng thời buộc hệ thống giải thích rõ catalog và thành phần thực thi quyền liên quan.

## Bài toán 2 — Kiểm tra ETL trên nhánh catalog trước khi công bố

**Cần giải quyết:** thay đổi dữ liệu trên nhánh riêng, kiểm tra xong mới đưa vào main. Walkthrough sử dụng Spark/Iceberg/Nessie trong Docker với warehouse cục bộ; có lệnh tạo bảng, tạo nhánh, truy vấn riêng và merge. [Walkthrough Dremio](https://www.dremio.com/open-source/nessie/).

**Thiết kế lab:** giới hạn ở ví dụ một bảng; ánh xạ môi trường tự quản lý cục bộ sang lựa chọn `on_prem` sẵn có. Đặt nhánh catalog là bắt buộc; không yêu cầu thêm FGAC/credential vending cho lab cô lập này. Các lựa chọn đó không khẳng định nhu cầu bảo mật của một doanh nghiệp hay khả năng thiếu của Nessie.

**Vì sao phù hợp:** kiểm tra trực tiếp nhánh đặc thù `branching`, khác với mục tiêu bảo mật của bài đầu. Tài liệu chính thức xác nhận thao tác nhánh/merge và lưu ý thay đổi cú pháp theo phiên bản. [Nessie SQL extensions](https://projectnessie.org/guides/sql/).

## Điền vào form hiện tại

Ký hiệu: **N** = nguồn nói trực tiếp; **S** = suy ra trong workload giới hạn; **T** = thiết kế thực nghiệm. Một ô có T không được trình bày như dữ kiện doanh nghiệp đã quan sát.

| Câu form | PUBLIC-LAB-01: phân quyền AWS | PUBLIC-LAB-02: nhánh catalog |
|---|---|---|
| I01 — nơi chạy | AWS — N | On-prem — T, đại diện lab cục bộ |
| I02 — engine | Spark — N | Spark — N |
| I03 — table format | Iceberg — N | Iceberg — N |
| I04 — số bảng | <100 — T; số cụ thể xem config | <100 — S; số cụ thể xem config |
| I05 — loại engine có thể cùng ghi | 1 — S, trong phạm vi Spark đã chọn | 1 — S, trong phạm vi Spark đã chọn |
| I07 — phân quyền đọc | Cả cột và hàng — N | Không có yêu cầu tại catalog — T |
| I08 — credential vending | Có — S; giữ đường truy cập dùng credential tạm thời | Không cần — T, cho warehouse cục bộ |
| I09 — nền tảng đã gắn bó | AWS-native — T, chỉ là bối cảnh theo chính sách hiện tại | Không — T |
| I10 — nhu cầu đặc thù | Không có nhu cầu bổ sung trong lab — T | Nhánh catalog / Bắt buộc — T về mức ưu tiên |

I06 đang bất hoạt nên không gửi. Không thêm field storage/API ngoài đặc tả. Nguồn nào không công bố tổng quy mô, hợp đồng hay thứ bậc ưu tiên thì vẫn được ghi là chưa biết trong bối cảnh gốc; lab bổ sung phạm vi công khai để tạo input thử nghiệm.

Payload điền tay hoặc chạy CLI:

- [PUBLIC-LAB-01.json](forms/PUBLIC-LAB-01.json)
- [PUBLIC-LAB-02.json](forms/PUBLIC-LAB-02.json)
- [PUBLIC-LAB-02-SOFT.json](forms/PUBLIC-LAB-02-SOFT.json): biến thể kiểm soát chỉ đổi rank của branching; không phải bài toán công khai thứ ba.

## Dùng trong phần thực nghiệm

1. Mô tả mục tiêu nghiệp vụ và dẫn nguồn, sau đó công khai các ô T/S. Không đưa tên catalog của bài gốc thành điều kiện bắt buộc của input.
2. Nạp payload qua cùng pipeline chính thức; lưu requirements Lớp 2 và JSON Lớp 3. Có thể nhập bảng trên vào form để xem giao diện; chưa có kiểm tra trình duyệt riêng cho hai hồ sơ mới trong đợt này.
3. Đối chiếu mục tiêu bài với yêu cầu phát sinh và trace. Các điểm cần xem đã ghi trước lần chạy trong `pre_run_checks` của casebook.
4. Với bài 2, so sánh thêm biến thể SOFT để thấy thay đổi do ưu tiên; giữ nguyên các dữ kiện khác, KB, trọng số và seed.
5. Báo cả kết quả chưa kết luận được. Tách tính đúng của luồng xử lý khỏi độ đúng của khuyến nghị thực tế.

Glue + Lake Formation và Nessie là **phương án tham chiếu**, không là nhãn đúng duy nhất. Hai nguồn đều là hướng dẫn của bên cung cấp/phát triển công nghệ, nên chưa đủ để tính accuracy hay chứng minh hệ thống chọn tốt hơn chuyên gia. Không nhập các hồ sơ mới vào tập hiệu chỉnh/kiểm tra đã khóa trước đây.

## Kết quả đã chạy và cách chạy lại

**Hai ca chính đều: 0 eligible / 7 conditional / 0 excluded.** Không có SOFT nên điểm và tỷ lệ đứng đầu là null. Biến thể SOFT có khoảng điểm [0, 1] cho cả bảy; chưa phân biệt được bằng bằng chứng đã xác lập. Xem [phân tích kết quả](results.md), [CSV theo ứng viên](results/candidate-results.csv) và [manifest kiểm chứng](results/run-manifest.json).

Chạy lại từ thư mục gốc dự án bằng môi trường Python hiện có:

```powershell
& 'C:/Users/Admin/miniconda3/python.exe' 'system-selection/research/catalog-reasoner-mvp/experiments/public-cases-2026-10-17/run_public_cases.py'
```

Script gọi hàm thuần của dự án, kiểm tra lặp với cùng seed, xác minh tham chiếu requirement/claim, và đối chiếu hash để đảm bảo không sửa runtime, KB, config hay bộ hồ sơ đã khóa. Đầu ra gốc giữ nguyên tại `results/<case-id>.json`; requirements tách riêng ở file cùng tên đuôi `.requirements.json`.

## Giới hạn phiên bản và phạm vi

Walkthrough AWS dùng release cũ hơn tài liệu sống hiện tại; hành vi credential khi ghi cần đối chiếu đúng release/operation. Ví dụ Docker Nessie cũng dùng bộ phiên bản cũ và image server không được pin đầy đủ; không coi đó là recipe triển khai hiện tại đã kiểm thử. Các version đã đọc được lưu trong [source-register.json](source-register.json).

Không đồng nhất catalog branch với Iceberg table branch; không suy giao dịch SQL nhiều bảng chỉ từ ví dụ một bảng. [Tài liệu giao dịch Nessie](https://projectnessie.org/guides/transactions/). Việc phân quyền nhiều tài khoản trong bài AWS cũng không tự tạo yêu cầu metadata federation.
