# Hệ thống hỗ trợ lựa chọn catalog

| Thành phần | Vai trò | Điểm bắt đầu |
| --- | --- | --- |
| `research/catalog-method-review/` | Tổng quan phương pháp lựa chọn, MCDA và benchmark | [Nghiên cứu phương pháp](research/catalog-method-review/README.md) |
| `research/catalog-selection-framework/` | Quy trình, biểu mẫu và protocol benchmark | [Framework](research/catalog-selection-framework/README.md) |
| `research/catalog-knowledge-base/` | Tri thức công nghệ, nguồn, registry và đặc tả input | [Knowledge base](research/catalog-knowledge-base/README.md) |
| `research/catalog-reasoner-mvp/` | Backend Python, kiểm thử, thí nghiệm và kết quả | [Bộ suy luận](research/catalog-reasoner-mvp/README.md) |
| `sites/catalog-review/` | Website và API gọi backend Python | [Website](sites/catalog-review/README.md) |

[Điểm vào MVP](CATALOG-MVP.md) liên kết hướng dẫn, báo cáo và giới hạn hiện tại. Nghiên cứu từng công nghệ và lab gốc được tập trung tại [technology-research](../technology-research/README.md).

Từ thư mục gốc workspace:

```powershell
Set-Location system-selection/sites/catalog-review
node server.mjs
```

Giữ `research/` và `sites/` cạnh nhau để bảo toàn đường dẫn giữa frontend, backend và knowledge base. Các đường dẫn `research/...` và `sites/...` trong manifest lịch sử được hiểu tương đối với thư mục `system-selection/` hiện tại.
