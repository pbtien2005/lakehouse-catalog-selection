# Form v3: storage và thao tác thực tế

Form v3 giữ ID và ý nghĩa I01–I10 của v2, I06 vẫn bất hoạt. Hai mục bổ sung giúp giữ thông tin đã biết trong bài toán. Không hỏi API, endpoint hoặc chi tiết connector mà architect chưa lựa chọn.

Registry máy đọc: `form-v3-registry.json`. Entry point thuần: `catalog_reasoner.intake_v3.normalize_form_v3(payload, assets)`. V2 vẫn dùng normalizer riêng, giữ hành vi tương thích.

| Mục | Đáp án | Xử lý |
| --- | --- | --- |
| I01 bổ sung | `local_lab` | Lab cục bộ/Docker, khác `on_prem`; không suy khả năng production. |
| I11 | `s3`, `adls_gen2`, `gcs`, `local_fs`, `hdfs`, `unknown` | Storage là dữ kiện độc lập với cloud. Khi cần vending, dùng storage cụ thể để thu hẹp qualifier. Thiếu/unknown vẫn cần làm rõ. |
| I12 | Object theo engine đã chọn ở I02; mỗi giá trị là danh sách `read`, `append`, `merge`, `overwrite`, `create_table`, hoặc riêng `unknown` | Mỗi cặp engine/thao tác tạo yêu cầu riêng. Không nhân chéo thao tác giữa engine. Thiếu thao tác không mặc định chỉ đọc. |
| `context.table_count_exact` | Số nguyên dương tùy chọn, phải thuộc bucket I04 | Thu hẹp demand HARD thành đúng số bảng. Thiếu số chính xác giữ nguyên khoảng HARD; không bỏ yêu cầu quota để làm kết quả đẹp. |

Ví dụ hợp đồng (minh họa input, không là dữ kiện doanh nghiệp):

```json
{
  "form_revision": "input-v3",
  "answers": {
    "I01": "local_lab",
    "I02": ["spark"],
    "I03": "iceberg",
    "I04": "lt_100",
    "I05": "one",
    "I07": "none",
    "I08": "no",
    "I09": ["none"],
    "I10": {"none": false, "selected": [{"feature": "branching", "rank": "mandatory"}]},
    "I11": "local_fs",
    "I12": {"spark": ["read", "append", "create_table"]}
  },
  "context": {"table_count_exact": 1}
}
```

Số bảng trên là demand của ví dụ, không là quota hoặc tham số tính điểm. Tất cả mức, trọng số, seed, ngân sách kịch bản và bucket vẫn đến từ config hiện hành; v3 không sửa chúng.

Khi lấy dữ kiện từ bài công khai, lưu riêng provenance theo từng đáp án: nguồn xác nhận / suy ra có căn cứ / lựa chọn thực nghiệm / chưa biết. Tài liệu không nói đến một nhu cầu không có nghĩa là nhu cầu đó bằng Không. Đưa một API từ claim vào đề xuất cần đường tích hợp có nguồn và tương thích toàn bộ workload, không chỉ vì claim đó làm ứng viên đạt.
