# Trạng thái bài Day 20 — Nguyễn Trường Bảo

Base track đã có đủ báo cáo và 5 screenshot thật. Sinh viên xác nhận đã review
tài liệu và nhận xét ngày 2026-10-06. Đã kiểm tra trực quan cả 5 ảnh.

## Kết quả

- Đủ hardware, manifest, benchmark hai quant và thread sweep.
- Đủ load 10/50 users trong 60 giây, metrics batching và saturation reading.
- Pipeline đủ 3 query, context, latency từng stage và khai báo real/stub.
- Đã bỏ nhãn bản nháp trong REFLECTION và 5 report sau xác nhận review.
- Smoke gốc tokens 0→38; lần chạy lại trong ảnh số 3 là 0→34.
- Đã sửa launcher Windows cho đường dẫn có khoảng trắng và kiểm thử server/smoke.
- Bonus chưa thực hiện; không bắt buộc cho 100 điểm base.

## Kiểm tra và nộp

Chạy `python scripts/verify.py` hoặc `.\lab.ps1 verify` nếu execution policy cho phép.
Verify kiểm tra file đang được Git track và nội dung local; phải commit và push
bản cuối để grader thấy đúng nội dung.

- [x] Sinh viên đã review tài liệu và nhận xét.
- [x] Đủ 5 screenshot thật.
- [x] Verify exit 0; đủ báo cáo và 5 screenshot được Git track.
- [ ] Push commit cuối lên GitHub.
- [ ] Xác nhận repo public và push trước deadline coach áp dụng.
- [ ] Paste URL vào VinUni LMS; cập nhật ngày nộp thực tế.

Chưa xác nhận push hoặc nộp LMS. Không commit models/*.gguf, runtime/, .venv/, .env.
