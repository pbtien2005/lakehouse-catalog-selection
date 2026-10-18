# Việc cần quyết sau khi hoàn thiện phần mềm

Không còn quyết định chặn triển khai phần mềm MVP. Trọng số, nhóm ứng viên, form và profile tiếp tục dùng các quyết định đã chốt. Không cần thêm câu hỏi hoặc chọn thuật toán mới.

**Hai quyết định quan trọng cho vòng sau:** (1) cho phép một vòng bổ sung/kiểm chứng KB theo đúng hợp đồng form; (2) nếu muốn kết luận chắc chắn, xác định cách người dùng hoặc profile xác nhận API/path được phép. Hiện chưa sửa claim nào và không thực thi candidate_bindings theo quyết định MVP. Nếu tiếp tục chỉ thử logic, có thể giữ nguyên trạng thái conditional và các giới hạn đã công khai.

Đây không chỉ là vấn đề thêm nhiều claim: qualifier API/path để mở còn có trường hợp chưa được bao phủ, nên dù các claim quan sát đều full cũng chưa đủ để kết luận vô điều kiện. Không tự coi tập API quan sát trong KB là một miền đầy đủ. Có thể xác nhận path/miền hữu hạn bằng hồ sơ kiểm chứng thủ công ở vòng sau; tự động tìm tổ hợp path là thay đổi phạm vi riêng, chưa thực hiện.

| Ưu tiên | Cần thu hoặc xác minh | Lý do |
|---|---|---|
| 1 | Quota bảng đúng boundary catalog và điều kiện áp dụng của từng scope | I04 không đổi kết quả hiện tại; không được thay quota schema/metastore/account bằng quota catalog |
| 1 | Các đường read/load thực tế, API/connector/edition/release và giới hạn | Null API/điều kiện đường truy cập còn mở; không tự chọn path để làm ứng viên đạt |
| 1 | Môi trường AWS/Azure/GCP/on-prem có bằng chứng đúng scope | Hướng dẫn local/standalone chưa đủ để kết luận production hoặc mọi cloud |
| 1 | Bằng chứng none khi thực sự không đáp ứng hợp đồng; không suy none từ việc không tìm thấy tài liệu | Bộ hồ sơ trên KB thật chưa tạo ca bị loại chắc chắn |
| 2 | Thực thi quyền đọc dữ liệu theo table/column/row và access path | Không đồng nhất read với authorize metadata hoặc filter/mask bằng cách đổi tên |
| 2 | Concurrent append/multi_engine và yêu cầu client/locking | Không đồng nhất với một claim Glue optimistic lock đơn lẻ |
| 2 | Atomic công bố metadata nhiều bảng; federation read_metadata theo nguồn | Không đổi nghĩa boundary/operation để ép khớp claim |
| 2 | Credential vending theo storage/client/edition | Không tự suy S3 từ AWS; giữ unknown nếu form không cung cấp storage |

Mỗi bổ sung cần scope, property, qualifier, level/value, điều kiện/limits và nguồn chính thức. Cần con người kiểm chứng claim trước khi thay KB. Sau khi thay dữ liệu, bảng quy đổi và hash phải được review lại; không dùng bộ holdout hiện tại để tinh chỉnh khuyến nghị. Nếu phát triển mô hình tiếp, lập bộ holdout mới trước vòng hiệu chỉnh.

[33 dòng ánh xạ và các khoảng trống](domain-mapping-review.md), [phiếu chấm chuyên gia không kèm kết quả](expert-score-sheet.html). Không cần chọn lại bảy ứng viên hoặc chốt thêm trọng số để hoàn thành MVP hiện tại.
