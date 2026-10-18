# Catalog Review — MVP đầu-cuối

UI hiện đọc registry form v3; API vẫn hỗ trợ payload v2 cũ. V3 thêm storage, thao tác từng engine, môi trường lab và số bảng chính xác tùy chọn. Submit gọi `POST /api/run`; server chỉ chuyển JSON qua stdin vào Python `catalog_reasoner.project_io`, không có evaluator quyết định JavaScript.

Chạy `node server.mjs` từ thư mục này, mở URL localhost được in ra. Cổng mặc định 4317 lấy từ `system-selection/research/catalog-reasoner-mvp/mvp-settings.json`. Nếu `python` không trỏ đúng Python 3, đặt `CATALOG_PYTHON` thành đường dẫn trình thông dịch. Server chỉ bind `127.0.0.1`; chưa triển khai public.

Chạy `npm test` và `npm run test:browser` để kiểm tra. Test API/browser cần truy cập localhost. Browser test dùng Playwright bundled của máy hiện tại; đặt `PLAYWRIGHT_MODULE` khi chuyển máy. Test hiện hành là `tests/e2e-v3.mjs`; kiểm tra v2 lịch sử giữ riêng ở `npm run test:browser:legacy`.

Ba nhóm, khoảng điểm, tỷ lệ kịch bản, regret, lý do và trace đều đọc từ Python. Unknown được giữ riêng; không có SOFT thì không tạo điểm hoặc người thắng. I06 bất hoạt. I09 chỉ là bối cảnh. Đã gỡ trường ngoài v2 và năm bậc ưu tiên cũ.

QA hiện hành: [e2e-v3.json](artifacts/e2e-v3.json), có payload thật, đường Nessie, native branching claim, lỗi trường, keyboard/focus, SOFT không bịa tỷ lệ thắng và màn 375px. Kết quả hiển thị profile, prerequisites, phiên bản, nguồn và giới hạn documented design feasibility. Không chứng nhận hạ tầng đã triển khai.

Xem [bản nâng chất lượng và bài thực nghiệm](../../research/catalog-reasoner-mvp/experiments/quality-upgrade-2026-10-18/README.md). Danh mục đường được rà soát hiện tập trung hai recipe; chưa chứng minh khuyến nghị tối ưu cho mọi bài toán hoặc cả bảy catalog.
