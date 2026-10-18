# Nhóm 3 — Benchmark hệ thống dữ liệu, tính đúng đắn và khả năng tái lập

Ngày tra cứu: 12/10/2026. Phạm vi: bốn nghiên cứu gốc bổ sung cho lựa chọn technical catalog; không phải khảo sát đầy đủ toàn bộ benchmark. Nhãn **Tác giả** chỉ nội dung nguồn; nhãn **Áp dụng/suy luận** là đề xuất của người tổng quan. Không chạy lại thực nghiệm của các bài.

## Bảng nguồn và mức đọc

| ID | Nguồn, tác giả, năm | DOI và toàn văn | Phần thực sự đọc |
|---|---|---|---|
| B1 | *Benchmarking Cloud Serving Systems with YCSB* — Brian F. Cooper, Adam Silberstein, Erwin Tam, Raghu Ramakrishnan, Russell Sears; SoCC 2010, pp.143–154 | [DOI 10.1145/1807128.1807152](https://doi.org/10.1145/1807128.1807152); [PDF bản bài gốc ở University of Athens](https://cgi.di.uoa.gr/~ad/M155/Papers/p143-cooper.pdf) | Abstract, §§1–5, mở đầu §6, §6.1, phần §6.6–7 từ text PDF được index, §9. Đọc PDF trực tiếp §§4–6.1,7.2,9; không đọc kỹ đồ thị §6.2–6.5. |
| B2 | *Rigorous Benchmarking in Reasonable Time* — Tomas Kalibera, Richard E. Jones; ISMM 2013, pp.63–74 | [DOI 10.1145/2464157.2464160](https://doi.org/10.1145/2464157.2464160); [Kent repository](https://kar.kent.ac.uk/33611/); [accepted manuscript đã chỉnh sửa](https://kar.kent.ac.uk/33611/45/p63-kaliber.pdf) | PDF Kent trang 2–4,10–12: abstract, §§1,3–4,9.3–12. §§6–9.2 chỉ thấy từng phần từ extraction/search; không tính đã đọc đầy đủ. Chưa đọc technical report chứa chứng minh. |
| B3 | *Elle: Inferring Isolation Anomalies from Experimental Observations* — Kyle Kingsbury, Peter Alvaro; PVLDB 14(3), pp.268–280; **2021 theo Reference Format của bài**, preprint 2020 | [DOI 10.14778/3430915.3430918](https://doi.org/10.14778/3430915.3430918); [PDF PVLDB](https://www.vldb.org/pvldb/vol14/p268-alvaro.pdf); [preprint ngày 23/03/2020](https://arxiv.org/abs/2003.10554) | Abstract, §3.1, đoạn §3.2.3 về recoverability, đoạn §3.3 về inferred graph/Theorem 3.1/soundness/completeness, §§4.2,5,6–6.1. Rà bổ sung §2.1 (trang in 269–270) về blind writes, traceability và recoverability. Không đọc liên tục toàn bộ §3, không kiểm chứng lại chứng minh hay mã nguồn. |
| B4 | *Scientific Benchmarking of Parallel Computing Systems: Twelve Ways to Tell the Masses when Reporting Performance Results* — Torsten Hoefler, Roberto Belli; SC 2015, Article73 | [DOI 10.1145/2807591.2807644](https://doi.org/10.1145/2807591.2807644); [PDF tác giả tại ETH](https://htor.inf.ethz.ch/publications/img/hoefler-scientific-benchmarking.pdf); [metadata ETH](https://www.research-collection.ethz.ch/entities/publication/3168b0c1-a308-4a57-8157-9d1764e58cd8) | Abstract, §2 phương pháp khảo sát, §§3–4, §5.2, §6 và 12 quy tắc. Chưa đọc sâu mô hình performance bounds §5.1. |

Bốn nguồn quan trọng đều được đọc ngoài abstract; không có nguồn chỉ đọc abstract được dùng làm căn cứ phương pháp.

## Ghi chú ngắn cho từng nguồn

### B1 — Thiết kế workload và so sánh hiệu năng

**Tác giả:** Bài toán là so sánh serving stores theo workload. YCSB tách workload, adapter và đo; thay đổi hỗn hợp thao tác, phân bố truy cập, tải để tạo đường latency–throughput và thử scaleup/elasticity. Kiểm chứng trên Cassandra, HBase, PNUTS, sharded MySQL.

**Giới hạn tác giả:** Core workloads không mô hình chính xác một ứng dụng và không phủ hết không gian hiệu năng; availability/replication là hướng tiếp theo. Kết quả phụ thuộc phiên bản, cấu hình và tuning.

**Áp dụng/suy luận:** Tái sử dụng cách tổ chức workload/adapter và tìm điểm bão hòa cho metadata. CRUD key-value không trực tiếp kiểm tra ngữ nghĩa commit Iceberg hoặc nhiều bảng; cần workload cùng oracle riêng.

### B2 — Số lần lặp và bất định

**Tác giả:** Bài toán là đạt độ chính xác với thời gian đo hữu hạn. Phương pháp mô hình hóa chi phí/variance ở nhiều mức lặp; dimensioning trước, rồi phân bổ repetitions và báo effect-size confidence interval. Kiểm chứng bằng DaCapo/SPEC CPU và so với heuristics.

**Giới hạn tác giả:** Thông số phải được xác định lại khi benchmark/platform thay đổi; kết quả dimensioning không dùng nguyên cho hệ thống khác. Nhận diện independence vững bằng tự động còn mở.

**Áp dụng/suy luận:** Pilot catalog cần tìm nguồn biến thiên ở request, run và service restart; không mặc định hàng nghìn request là hàng nghìn mẫu độc lập. Ba lần chạy chỉ là điểm khởi đầu, không bảo đảm precision; percentile đuôi cần phân tích riêng.

### B3 — Kiểm tra tính đúng đắn từ quan sát

**Tác giả:** Elle suy dependency graph từ lịch sử client và phát hiện chu trình bất thường. Soundness gắn với traceability/recoverability và datatype; kiểm chứng bằng lập luận hình thức, bốn database thực và đo checker so với Knossos.

**Giới hạn tác giả:** Bỏ predicate anomalies; completeness chỉ chứng minh ở trường hợp đặc biệt, quan sát thiếu có thể bỏ sót lỗi. Một số chứng minh chỉ tóm tắt trong bài.

**Áp dụng/suy luận:** Ghi mã thao tác, invocation/completion, kết quả và trạng thái indeterminate để tạo bằng chứng phản ví dụ. Trước khi dùng Elle phải chứng minh mapping đối tượng/transaction sang model của nó. Catalog commit một bảng, branch commit nhiều bảng và SQL transaction có ranh giới khác nhau; không tự coi chúng tương đương. Không thấy anomaly không chứng minh hệ thống luôn đúng.

### B4 — Thiết kế và công bố thí nghiệm

**Tác giả:** Khảo sát ngẫu nhiên phân tầng 120 bài, có 25 bài không áp dụng; đánh giá reporting, minh họa bằng HPC measurements, rồi đề xuất 12 quy tắc và LibSciBench. Yêu cầu mô tả factors/setup, variation, cách đo, cold/warm state, tránh cherry-picking; chỉ số trung tâm có thể thiếu thông tin về latency đuôi.

**Giới hạn tác giả:** Đánh giá interpretability trong khảo sát là nhận định chủ quan; không thể có bộ quy tắc đầy đủ cho mọi nghiên cứu. Phạm vi chính là parallel/HPC interval measurements.

**Áp dụng/suy luận:** Với catalog, công bố software/backend/client, workload/seed, cache, mạng, retry, raw history và script phân tích. Khi managed service không tái tạo hạ tầng được, ghi điều kiện quan sát và ưu tiên khả năng diễn giải; không suy rằng kiểm soát lab chứng minh production behavior.

## Tổng hợp dành cho đề tài — đề xuất của người tổng quan

Benchmark là một đường cung cấp bằng chứng cho yêu cầu đã nêu; không tự tạo đầy đủ các tiêu chí hay lựa chọn phương pháp MCDA.

Thiết kế tối thiểu nên gồm:

1. **Performance:** workload đại diện có thao tác metadata rõ; tách workload, adapter, hệ thống và phép đo. Tăng tải và quy mô metadata; giữ hoặc công khai khác biệt về ngữ nghĩa, durability, auth và retry.
2. **Correctness:** xác định bất biến theo đúng hợp đồng thao tác trước. Với workload append-only có ID duy nhất, đối chiếu tập kết quả hợp lệ để tìm cập nhật mất hoặc lặp. Với overwrite/delete, giá trị cũ có thể biến mất hợp lệ; phải kiểm tra lịch sử và quan hệ phụ thuộc, không yêu cầu mọi giá trị từng commit còn ở trạng thái cuối. Phân biệt failed với indeterminate và xác định hiệu ứng cần kiểm tra cho từng loại kết quả. Conflict hợp lệ không phải lost update.
3. **Statistical interpretation:** pilot tìm warm-up, trend và mức độc lập; báo các lần chạy, variation và khoảng sai số phù hợp với chỉ số. Nếu không đủ tài nguyên đạt precision đã định, trả về kết quả bất định.
4. **Reproducibility:** lưu manifest cấu hình, phiên bản, dữ liệu sinh/seed, log thao tác, script và protocol. Ghi điểm không kiểm soát được; không chỉ lưu ảnh đồ thị.

Chỉ benchmark các phương án có cùng thao tác và khả năng cần dùng. Ánh xạ **yêu cầu → bài thử/oracle → kết quả có điều kiện → quyết định**. Trước benchmark, ghi điểm nào đang thiếu bằng chứng và khuyến nghị tạm thời; sau benchmark, kiểm tra điều gì thay đổi. Lợi thế latency nhỏ hơn sai số hoặc không thay đổi mức đáp ứng không nên tạo một kết luận lựa chọn chắc chắn.

Không nguồn nào ở nhóm này xác nhận một catalog “tốt nhất”, cung cấp trọng số chọn catalog, hay chứng minh phương pháp mới. Muốn kết luận cho Polaris/HMS/Glue/Nessie/Gravitino/Unity Catalog cần thêm hợp đồng chính thức đúng phiên bản, cấu hình và yêu cầu thực tế.

## Nhật ký tìm kiếm và sàng lọc

Các truy vấn đã chạy:

- `Cooper Silberstein Tam Ramakrishnan Sears 2010 Benchmarking cloud serving systems YCSB pdf`
- `Kalibera Jones 2013 Rigorous Benchmarking in Reasonable Time pdf`
- `Kingsbury Alvaro Elle Inferring Isolation Anomalies Experimental Observations 2020 pdf DOI`
- `Hoefler Belli 2015 Scientific Benchmarking Parallel Computing twelve ways tell masses reporting performance pdf`
- Các truy vấn theo tên/filename để tìm full text khi endpoint PDF lỗi.

Giữ B1 vì framework workload có kiểm chứng nhiều stores; B2 vì mô hình lặp/uncertainty; B3 vì correctness oracle có điều kiện hình thức; B4 vì reproducibility/reporting được khảo sát và minh họa thực nghiệm.

Không dùng SciSpace/Rankless/blog/slides/Wikipedia làm căn cứ nội dung kỹ thuật; chỉ dùng kết quả để tìm bài gốc. Bản YCSB ở Albany và website tác giả không fetch được, dùng bản nguyên bài ở University of Athens. Kent/CiteSeer lúc đầu lỗi; sau đó Python urllib với User-Agent tải được manuscript Kent, nhưng lần đọc bổ sung bị timeout. Ranh giới đọc trong bảng phản ánh phần output thực sự xem được, không phải toàn bộ PDF đã tải.

Dừng khảo sát nhóm này: đã đủ căn cứ phân biệt workload measurement, correctness checking, statistical repetition và reproducibility. Còn thiếu để chốt protocol catalog: quy mô/tải mục tiêu, hợp đồng commit/consistency của cấu hình ứng viên, tài nguyên lab, ngưỡng yêu cầu và mức bất định chấp nhận.
