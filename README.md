# Nghiên cứu catalog cho Data Lakehouse

Workspace gồm nghiên cứu công nghệ, lab thực hành và hệ thống hỗ trợ lựa chọn catalog.

| Thư mục | Nội dung | Điểm bắt đầu |
| --- | --- | --- |
| `technology-research/` | Nghiên cứu từng công nghệ, lab, mã nguồn và tài liệu tham khảo | [Danh mục công nghệ](technology-research/README.md) |
| `system-selection/` | Phương pháp lựa chọn, knowledge base, backend suy luận và website | [Hệ thống lựa chọn](system-selection/README.md) |
| `deliverables/` | Báo cáo, slide, ghi chú thuyết trình và nguồn dựng slide | [Danh mục đầu ra](deliverables/README.md) |
| `archive/` | File tạm, log cũ và bảng đối chiếu đường dẫn khi sắp xếp | [Lưu trữ](archive/README.md) |

## Cấu trúc

```text
technology-research/
  apache-polaris/
    docs/                         # 7 chương nghiên cứu kiến trúc
    polaris-source-1.7.0/         # Checkout Git tham khảo
  apache-gravitino/{lab,references}/
  aws-glue-data-catalog/
  hive-metastore/lab/
  project-nessie/lab/
  unity-catalog/{lab,unitycatalog-v0.6.0}/
system-selection/
  research/
    catalog-method-review/
    catalog-selection-framework/
    catalog-knowledge-base/
    catalog-reasoner-mvp/
  sites/catalog-review/
  CATALOG-MVP.md
deliverables/
  catalog-6-slides-viettel/
  catalog-metadata-vdt/
  .build/                         # Script, nguồn và kết quả trung gian dựng slide
archive/
  logs/
  tmp/
```

## Chạy hệ thống lựa chọn

Từ thư mục gốc workspace, dùng Python 3 và Node.js:

```powershell
Set-Location system-selection/sites/catalog-review
node server.mjs
```

Mở địa chỉ localhost server in ra, mặc định `http://127.0.0.1:4317`. Có thể đặt `CATALOG_PYTHON` nếu cần chọn trình thông dịch Python. Xem [hướng dẫn MVP](system-selection/CATALOG-MVP.md) và [giới hạn của kết quả](system-selection/research/catalog-reasoner-mvp/outputs/mvp/limitations.md).

Kiểm thử từ thư mục gốc, thực hiện từng nhóm riêng:

```powershell
Push-Location system-selection/research/catalog-reasoner-mvp
python -m pytest
Pop-Location

Push-Location system-selection/sites/catalog-review
npm test
Pop-Location
```

## Quy ước bổ sung nội dung

- Tài liệu và lab công nghệ đặt trong `technology-research/<ten-cong-nghe>/`; giữ các file Compose, cấu hình và script cùng lab.
- Phương pháp, dữ liệu và mã của hệ thống lựa chọn đặt trong `system-selection/`; giữ `research/` và `sites/` cạnh nhau vì có liên kết tương đối.
- Đầu ra để đọc hoặc trình bày đặt trong `deliverables/`; nguồn dựng slide nằm ở `deliverables/.build/`.
- File tạm và log cũ đặt trong `archive/`. Các output kiểm chứng gắn với một thí nghiệm vẫn đi cùng thí nghiệm đó.

`.vscode/` và `.github/` giữ cấu hình công cụ ở gốc. Repo Git chính quản lý tài liệu, lab và hệ thống lựa chọn. Hai checkout tham khảo Polaris và Unity Catalog chỉ lưu local, được giữ nguyên lịch sử và loại khỏi bản nộp bằng `.gitignore`.

Đợt sắp xếp ngày 18/10/2026 có [bảng ánh xạ đường dẫn cũ → mới](archive/reorganization-2026-10-18.json). Các manifest và báo cáo kiểm chứng lịch sử có thể ghi đường dẫn tại thời điểm được tạo.

## Phạm vi bản nộp Git

`.gitignore` ở gốc loại `deliverables/`, `archive/`, hai checkout mã nguồn upstream, cấu hình IDE, thông tin môi trường riêng, dependency, cache và kết quả kiểm thử tạm. Các thư mục đó vẫn có thể tồn tại trong workspace local nhưng không nằm trong bản nộp. Một số liên kết tới đầu ra local hoặc mã nguồn tham khảo trong tài liệu vì vậy chỉ dùng được trên workspace đầy đủ.

Bản nộp giữ tài liệu nghiên cứu, lab và script thiết lập, cấu hình mẫu như `.env.example`, knowledge base, mã suy luận, kiểm thử, báo cáo/thí nghiệm nghiên cứu và `package-lock.json`. Riêng `system-selection/sites/catalog-review/dist/` được giữ vì đây là frontend server đang phục vụ.

Mã nguồn upstream có thể lấy lại từ repository [Apache Polaris](https://github.com/apache/polaris) và [Unity Catalog](https://github.com/unitycatalog/unitycatalog); chọn phiên bản/commit theo tài liệu nghiên cứu tương ứng. Các lab dùng cấu hình và hướng dẫn trong thư mục `lab/` của từng công nghệ.
