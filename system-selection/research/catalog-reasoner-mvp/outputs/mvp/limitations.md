# Giới hạn kiểm chứng MVP

**Đã chứng minh trong các ca đã chạy:** luồng form v2 → Lớp 2 → Lớp 3 → UI thực thi được; validation chặn lỗi input; property/qualifier/rubric được kiểm tra; thiếu claim giữ unknown; HARD có ba trạng thái; điểm SOFT tuyệt đối; sampling tái lập theo seed; excluded không vào ranking; kết luận có requirement/claim trace. Đây là bằng chứng kiểm thử, không là chứng minh toán học cho mọi đầu vào.

**Chưa chứng minh:** claim trong KB đúng/đủ/còn hiện hành; khuyến nghị phù hợp thực tế; hiệu năng/khả năng production của catalog; độ chính xác của tỷ lệ kịch bản. Chưa có đánh giá chuyên gia. KB giữ nguyên, phần lớn bằng chứng có status draft. Trên bộ 10 hồ sơ đã khóa, 9 ca hợp lệ đều có 7 conditional, không có eligible/excluded chắc chắn. Đây là thiếu độ phủ bằng chứng, không phải “các catalog đều như nhau”.

**Mọi mặc định/giả định hiện dùng:** I01–I03 cụ thể HARD/full theo cờ true; nice-to-have lấy low=1 và weight_defaulted; thang none/partial/full=0/0,5/1; high/low=3/1; max_scenarios=500, seed=42. Đếm bảng theo [0,99], [100,999], [1000,10000], [10001,null] trong một catalog. Profile: read/load metadata, concurrent append/multi_engine, nhánh catalog, atomic catalog_metadata_commit, federation read_metadata. Không suy storage từ cloud. I06 bất hoạt, I09 chỉ bối cảnh. Candidate bindings chỉ trace.

Unknown support điền theo rubric; thiếu cell KB được giả định độc lập, format/storage chưa rõ chia sẻ giữa ứng viên. Đồng hạng chia đều credit. Sampling có cặp phản thực, phụ thuộc giữa các lượt nhưng miền biên lấy đều; ngân sách ảnh hưởng mặc định 0,5 nằm trong tổng tối đa 500. Regret khi sampling là cực đại quan sát kèm cận trên bảo thủ; utility khi không khả thi=0. Không SOFT thì không có điểm/người thắng. Thiếu weight dùng default_weight_rank=low. Unknown trong form không bị coi là không cần.

Độ nhạy chỉ tập hiệu chỉnh: ±30%, 1.000 lượt/ca hợp lệ có SOFT, thay một weight mỗi lượt, dùng chung kịch bản và seed 42. Tập 6/4 được khóa trước; không dùng kết quả holdout để tối ưu. Transport: cổng mặc định 4317, request 65536 byte, output 16777216 byte, timeout 30000 ms, tối đa một request đang chạy. Giá trị và metadata assumption nằm trong ba file config và được ghi trong JSON đầu ra. Cổng demo có thể do hệ điều hành cấp khi cổng mặc định đã dùng.

**Cố ý hoãn:** xác minh/bổ sung KB, đánh giá chuyên gia, joint path resolver, bật streaming, câu hỏi mới, tiêu chí vận hành/lock-in/authentication, hiệu chỉnh trọng số bằng chuyên gia, deploy public/xác thực. Các kết quả không hỗ trợ quyết định mua/triển khai thực tế trước khi kiểm chứng KB.
