# Nguồn sát catalog và tài liệu chính thức

Ngày đối chiếu: 12/10/2026. Đây là ghi chú nguồn cho tổng quan phương pháp, không phải đánh giá tính năng toàn diện hoặc kết quả chạy benchmark. Đọc tài liệu không đồng nghĩa kiểm chứng runtime. Các trang `latest`, `develop` và nhánh `main` có thể thay đổi; khi thực nghiệm cần ghim phiên bản/commit phù hợp.

## Nghiên cứu gốc sát miền catalog

| Mã | Nguồn, tác giả, năm | DOI / URL | Phần thực sự đã đọc |
|---|---|---|---|
| S5 | *Reproducible data science over data lakes: replayable data pipelines with Bauplan and Nessie* — Jacopo Tagliabue, Ciro Greco (2024) | [arXiv DOI 10.48550/arXiv.2404.13682](https://doi.org/10.48550/arXiv.2404.13682); [HTML v1](https://arxiv.org/html/2404.13682v1) | Abstract, §§1–5 và §7; Table 1; nội dung captions Figures 1–4 và Listings 1–3. Không phân tích trực quan ảnh, không đọc toàn bộ tài liệu tham khảo. Đây là bản preprint v1; tác giả ghi accepted at DEEM/SIGMOD2024. Không dùng DOI conference placeholder trong HTML. |

**S5 — Tác giả:** giải quyết tái lập pipeline qua versioning code/data và runtime cloud; giải thích kiến trúc Bauplan–Nessie, minh họa debug/replay bằng CLI. Table 1 nêu data, code, runtime, hardware. **Giới hạn quan sát từ phần đã đọc:** minh họa workflow, không có benchmark so sánh catalog hay kiểm chứng định lượng tính tái lập trên nhiều triển khai. **Suy luận áp dụng:** branch/replay có giá trị khi yêu cầu pipeline cần chúng; bằng chứng này không xếp Nessie trên catalog khác. Tái lập thí nghiệm cần giữ cả trạng thái dữ liệu, workload, code và môi trường; không chỉ image catalog. Runtime Bauplan không đại diện cấu hình Viettel, và branch không tự bảo đảm mọi pipeline deterministic.

## Tài liệu chính thức xác minh ngữ nghĩa và phạm vi công nghệ

Tác giả của D1–D7 là các dự án/tổ chức đứng tên tài liệu, không phải nhóm tác giả bài nghiên cứu. Năm publication không được suy ra từ năm truy cập. Không có thí nghiệm của tổng quan này với các sản phẩm.

| Mã | Tên, tổ chức, năm/phiên bản nguồn | URL trực tiếp | Phần thực sự đã đọc | Nội dung xác minh; giới hạn; áp dụng (suy luận) |
|---|---|---|---|---|
| D1 | *REST Catalog Spec* và *rest-catalog-open-api.yaml* — Apache Iceberg/ASF; nhánh `main` tại ngày truy cập | [Overview](https://iceberg.apache.org/rest-catalog-spec/); [OpenAPI](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml) | Overview: REST Catalog API Specification/Protocol. YAML đọc trực tiếp đoạn `updateTable`, requirements/updates và error responses; phần đầu `commitTransaction`, không đọc toàn bộ YAML. | Contract phân biệt conflict với commit state unknown; có mô tả atomic multi-table operation. Chưa xác nhận mỗi server triển khai tất cả endpoints. Suy luận: oracle phải phân biệt commit bị từ chối, được xác nhận và chưa xác định; không coi timeout mặc định là abort. |
| D2 | *Polaris Benchmarks* — Apache Polaris/ASF; README nhánh `main` | [README](https://github.com/apache/polaris-tools/blob/main/benchmarks/README.md) | Available Benchmarks, Parameters: Dataset Structure Parameters; không audit toàn bộ Gatling implementation. | Có workload tạo/đọc/cập nhật cây namespace/table/view, commit và workload có tranh chấp. Đây là công cụ Polaris, chưa là benchmark so sánh sáu catalog hoặc oracle correctness. Suy luận: tái dùng cấu trúc workload, phải kiểm chứng adapter và ngữ nghĩa trước khi chuyển công nghệ. |
| D3 | *Iceberg REST Catalog API backed by Hive Metastore* — Apache Hive/ASF; trang cập nhật 14/11/2025, đường `latest` | [HMS REST](https://hive.apache.org/docs/latest/admin/iceberg-rest-catalog/) | Introduction, Basic configurations, Authentication, Authorization và Minimal Setup examples. | HMS có đường Thrift và REST trong tài liệu được đọc; xác thực/phân quyền cần cấu hình. Chưa xác minh runtime của phiên bản lab. Suy luận: so sánh endpoint/client cụ thể, không gán một đặc tính giao thức cho mọi phiên bản HMS. |
| D4 | *AWS — Optimistic Locking* — Apache Iceberg/ASF, docs 1.7.1 | [AWS integration](https://iceberg.apache.org/docs/1.7.1/aws/#optimistic-locking) | Toàn bộ tiểu mục Optimistic Locking và ghi chú SDK; không đọc toàn bộ hướng dẫn AWS. | GlueCatalog sử dụng version ID; mismatch dẫn tới refresh, conflict check và retry khi hợp lệ. Ghi chú SDK tối thiểu 2.17.131. Không suy rộng sang Glue REST hoặc mọi engine. Suy luận: client/SDK là biến cần ghim khi thử concurrency. |
| D5 | *Iceberg REST Catalog Service* — Apache Gravitino/ASF; README nhánh `main` | [IRC documentation](https://github.com/apache/gravitino/blob/main/docs/iceberg-rest-service.md?plain=1) | Deployment Modes; Catalog Backend Configuration: Hive/JDBC/REST; Access Control Prerequisites/Flow. | Backend và deployment mode thay đổi trách nhiệm; tài liệu nêu authorization IRC cần auxiliary mode và cấu hình tương ứng. Chưa kiểm chứng chạy thật, không áp claim nhánh main vào release cũ. Suy luận: so sánh cấu hình kiến trúc, kiểm tra nơi thực thi quyền thay vì chỉ đánh dấu RBAC có/không. |
| D6 | *Unity Catalog with UniForm tables* — Unity Catalog project; trang cập nhật 05/05/2025 | [UniForm usage](https://docs.unitycatalog.io/usage/tables/uniform/) | Overview, Read Delta Uniform tables via Iceberg REST Catalog, Setting up REST Catalog with Apache Spark. | Trang chứng minh đường đọc Delta UniForm từ Iceberg client. Không đủ chứng minh ghi/commit native Iceberg. Suy luận: chia khả năng theo thao tác, không suy từ đọc được sang ghi được; nguồn này không phải audit mọi tính năng Unity Catalog OSS. |
| D7 | *Nessie Specification* — Project Nessie; đường `develop` | [Specification](https://projectnessie.org/develop/spec/) | Operations in a Nessie commit; Mapping SQL DDL; Put/Delete/Unmodified; Conflict Resolution. | expectedHash/conflict xét content key; nhánh đổi do key khác không mặc định từ chối. Không xác minh hành vi client/version/runtime. Suy luận: oracle tranh chấp cùng key và khác key phải khác; không dùng rule đơn giản “HEAD đổi thì mọi commit thất bại”. |

## Nhật ký tìm kiếm bổ sung sát miền catalog

| Truy vấn / thao tác | Kết quả và quyết định |
|---|---|
| `"Iceberg" "catalog" "benchmark" research evaluation` | Có nhiều bài đo engine/table format và practitioner posts. Không dùng chúng làm nghiên cứu gốc về phương pháp lựa chọn catalog. |
| `"catalog selection" "Iceberg" paper methodology` và `"metadata catalog" "benchmark" Polaris Nessie research` | Có bài hướng dẫn lựa chọn thương mại/practitioner và một preprint về proof-gated publication. Không đọc sâu các nguồn này; không dùng để kết luận phương pháp thắng. Không suy ra không tồn tại nghiên cứu lựa chọn catalog. |
| `Nessie specification atomic commit references projectnessie.org` | Tìm được D7 và S5 qua nội dung data-lake reproducibility; loại các bài Nessie khác miền (RDMA, astronomy, JavaScript). |
| Mở arXiv S5 metadata và HTML §§1–5,7 | Giữ nghiên cứu workflow sát catalog để kiểm tra giới hạn chuyển miền. Không coi demo là comparative benchmark. |
| Mở D1–D7 và đọc các phần ghi trong bảng | Giữ các claim hẹp có thể kiểm chứng. URL Nessie `/nessie-latest/spec/` và raw Gravitino tag đoán `gravitino-1.3.1` không truy cập được; chuyển sang URL chính thức đã tìm thấy, không gán nhầm phiên bản. |

## Ranh giới sử dụng

Nguồn chính thức xác minh contract, khả năng được tài liệu hóa và phụ thuộc cấu hình. Chúng không cung cấp bằng chứng rằng một phương pháp MCDA phù hợp, catalog đạt hiệu năng production hoặc đem lại tiết kiệm cho Viettel. S5 bổ sung yêu cầu tái lập pipeline nhưng không cung cấp benchmark lựa chọn catalog. Những claim cần bản release ổn định và runtime test được để lại cho giai đoạn thực nghiệm.
