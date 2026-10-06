# Reflection — Day 20 Lab

> Báo cáo được Codex hỗ trợ từ số liệu đo thật. Nguyễn Trường Bảo đã xác nhận
> review tài liệu và nhận xét §2–5 ngày 2026-10-06.

- **Họ tên:** Nguyễn Trường Bảo
- **MSSV:** 2A202602540
- **Cohort:** K4-L3
- **Ngày chuẩn bị báo cáo:** 2026-10-06 (UTC+7). Chưa nộp LMS; cập nhật ngày submit thực tế khi nộp.

## 1. Hardware & runtime

- OS: Windows 11 AMD64; Python 3.12.6.
- CPU: Intel Core i5-11300H @3.10 GHz; 4 core physical / 8 logical.
- CPU extensions: chưa đo riêng; không suy ra AVX flags từ tên CPU.
- RAM: 15,7 GiB; hardware probe và psutil cho cùng kết quả.
- GPU lắp trong máy: RTX 3050 Laptop 4096 MiB. **Inference thực tế: CPU, ngl=0**.
- Runtime: llama.cpp b10488; asset llama-b10488-bin-win-cpu-x64.zip.
- Model: Qwen3.5 0.8B; LAB_MODEL=qwen35-0.8b; Q4_K_M + UD-Q2_K_XL.
- Môi trường: laptop local. Settings chung: threads=4, ctx=2048, parallel=4,
  continuous batching và metrics bật, reasoning=off. Bench max_tokens=64;
  load short/long max_tokens=48/96; pipeline max_tokens=200.

Setup story: CIM bị Access denied làm probe cũ đọc sai RAM. Đã dùng registry/Windows
API để đo đúng. CUDA download timeout nên dùng CPU prebuilt; CPU ZIP được tải tiếp và
kiểm tra checksum ZIP thành công. Hai GGUF Qwen tải qua mirror, kiểm tra magic GGUF
và đủ dung lượng. Runtime/model hoàn chỉnh rồi mới tạo manifest và chạy inference.

## 2. Đo lường

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| Q4_K_M | 0.50 | 2625 | 347 / 413 | 27.6 / 31.7 | 2083 / 2329 / 2329 | 36.3 |
| UD-Q2_K_XL | 0.39 | 2434 | 395 / 462 | 27.3 / 29.0 | 2105 / 2251 / 2251 | 36.6 |

**Quan sát:** Q2 decode nhanh hơn khoảng 0,8% và nhỏ hơn 0,11 GiB; chưa có lợi ích tốc độ rõ. Đã hỏi cùng câu trên cả hai. Câu dài bị cắt ở 200 token; khi yêu cầu ngắn, cả hai vẫn nhầm goodput với data rate, Q2 còn trả ví dụ sai. Đề xuất giữ Q4, kiểm tra factuality trước sử dụng.

Warm-up bị loại; mỗi quant có 10 request thành công. TTFT đo ở client tới content
đầu tiên, gồm HTTP/scheduling/prefill; TPOT dùng output token count của server.
P95=P99 ở n=10 theo nearest-rank. Chênh lệch tốc độ
1.008× chưa vượt nhiễu
của một lần chạy. Hai lượt chất lượng lưu nguyên trong 01-quality-comparison.json.

## 3. Serving under load

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 31 | 0.54 | 16000 | 22000 | 23000 | 8.4 | 0.0% |
| 50 | 44 | 0.76 | 29000 | 52000 | 57000 | 21.6 | 0.0% |

- Users tăng 5×; throughput tăng 1.41×; P95 tăng 2.36×.
- Effective concurrency ở 50 users: 21.6 so với 4 slots.
- Peak sampled busy slots: 3,86/4; processing=4; deferred peak=46.
- Smoke: tokens_predicted_total tăng 0→38; /v1/chat/completions trả completion thật.

**Saturation reading:** RPS tăng 1.41×, P95 tăng 2.36×; deferred tới
46, effective concurrency 21.6>4. Server có queueing; không định vị được knee
chính xác vì chỉ đo 10/50 users. Đề xuất giới hạn admission/concurrency để bảo vệ
SLO E2E P95≤30 giây, đo cả rejected requests. Không tăng threads vì thread sweep
đã đạt đỉnh ở 4; tăng parallel có thể kéo dài decode/KV pressure.

SLO minh họa: E2E P95 ≤ 30 giây (không phải SLO TTFT/TPOT). Run 10 users đáp ứng; run 50 users không đáp ứng. Với 10 users, max E2E của mọi request hoàn tất <30 giây, nên observed goodput E2E@30s bằng RPS 0,54. Với 50 users, CSV percentile không cho phép tính chính xác số request đạt 30 giây; không suy ra goodput chính xác từ aggregate RPS. Cần histogram/per-request log cho con số đó.

Chỉ chạy 60 giây/run, với 31 và 44 request hoàn tất. P95/P99 là xấp xỉ Locust, không phải phân phối ổn định đã hội tụ. Request còn đang chờ khi test dừng không nằm trong completed-request stats; 0 failures không có nghĩa mọi request khởi tạo đã hoàn tất. Little’s Law là ước lượng cho cửa sổ hữu hạn có censoring. 5× là số users trong closed-loop test, không phải arrival RPS đo được tăng chính xác 5×. Có queueing ngay ở 10 users (effective concurrency 8,4 >4); không xác định knee chính xác vì không có các điểm dưới 10.

## 4. Integration

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | localhost, không kết nối cloud/IaC | stub |
| N17 Data pipeline | TOY_DOCS trong bộ nhớ | stub |
| N18 Lakehouse | Python list thay lakehouse | stub |
| N19 Vector + features | keyword overlap, không embedding server | stub |
| N20 Serving | llama-server b10488, CPU | real; chạy hết 3 query |

Mean của 3 query:

- embed: 0.0 ms (không gọi embedding model).
- retrieve: 0.1 ms.
- llm: 6525.5 ms.
- total: 6525.6 ms.
- Stage lớn nhất: llm, 99.998% total (report làm tròn 100%).

**Reflection:** LLM chiếm gần toàn bộ latency; stage này gồm HTTP, scheduling,
prefill và decode. Đề xuất rút ngắn output rồi đo lại chất lượng; CUDA là một
experiment tiếp theo. Không thể khẳng định giảm latency 2× trước khi đo.
SYSTEM_PROMPT giữ nguyên từng byte; chưa đo độc lập hiệu quả prefix cache.

Hai lượt comparison dùng cùng prompt/settings cho từng cặp (temperature=0, seed=42, max_tokens=200). Lượt đầu cả hai finish_reason=length; lượt ngắn finish_reason=stop. Hai cặp câu hỏi không đủ kết luận chất lượng chung do quantization. Smoke trả completion và metrics đúng, nhưng định nghĩa goodput của model sai. RAG cũng bịa tên đầy đủ TTFT/TPOT và trộn prefix caching với disaggregated serving. Giữ nguyên raw output để đánh giá; không sửa câu trả lời nhằm làm đẹp kết quả.

## 5. The single change that mattered most

**Change trong sweep kiểm soát:** tăng -t từ 1 lên 4, trên cùng Q4_K_M, CPU,
llama-bench tg128, 2 repetitions mỗi điểm.

```text
before:  14.34 tok/s (-t 1)
after:   34.13 tok/s (-t 4)
speedup: 2.38×
```

Một luồng chưa tận dụng đủ 4 core vật lý để xử lý các phép toán decode. Khi tăng
lên 4 luồng, công việc được chia cho nhiều core; throughput tăng 2.38×, chưa
đạt tuyến tính 4× vì vẫn có phần tuần tự và tài nguyên bộ nhớ dùng chung. Knee
nằm ở 4 luồng: 8 luồng đạt 33.84 tok/s so với 34.13 ở 4 luồng.
SMT chia sẻ execution resources; thêm luồng không bổ sung memory channel.

16 luồng chỉ đạt 25.01 tok/s, phù hợp với oversubscription, scheduling và
tranh chấp tài nguyên. Không đo bandwidth/performance counters nên đây là cơ chế
phù hợp dữ liệu, chưa chứng minh bandwidth là nguyên nhân duy nhất. Default của
lab đã là 4 luồng: speedup so với default là 1,00×. 2.38× là so với cấu hình
1 luồng thực sự đã đo, không phải tuyên bố tối ưu default thêm 2.38×.

## 6. Bonus

Không làm bonus; tập trung hoàn tất base.

## 7. Kết quả review

Hai quant gần ngang tốc độ nhưng output có factual errors; chạy API thành công
không đồng nghĩa câu trả lời đúng. Đã review raw answers; kết luận chất lượng chỉ áp dụng cho các câu hỏi đã đo. N16–N19 vẫn stub, không phải stack thật của các ngày trước.

## 8. Self-check trước khi push

- [x] Hardware, manifest, baseline, tune, hai load CSV, metrics và pipeline đã tạo.
- [x] Các số trong báo cáo lấy từ JSON/CSV; giữ nguyên bảng generated report.
- [x] Khai báo CPU inference, các stub và việc dùng AI.
- [x] Sinh viên đã review tài liệu, lập luận và chất lượng câu trả lời.
- [x] Đủ 5 screenshot thật ở submission/screenshots; đã kiểm tra trực quan.
- [x] Verify exit 0 với báo cáo và 5 screenshot được Git track; commit bản cuối trước khi push.
- [ ] Kiểm tra repo public, push và paste URL vào LMS theo deadline coach.

## 9. Khai báo sử dụng AI

Dùng OpenAI Codex để đọc đề/rubric, sửa lỗi Windows, hỗ trợ setup, chạy benchmark,
load test/metrics và pipeline, tổng hợp số liệu đo thật và soạn bản nháp nhận xét.
Sinh viên đã xác nhận review tài liệu và §2–5 ngày 2026-10-06; không dùng số liệu hoặc screenshot
giả. Chưa dùng cloud, chưa push hay nộp LMS trong phiên này.

## 10. Bằng chứng screenshot

| Ảnh | Nội dung |
|---|---|
| [01-hardware-probe.png](screenshots/01-hardware-probe.png) | CPU, RAM, GPU, model và runtime |
| [02-bench.png](screenshots/02-bench.png) | Hai quant, TTFT/TPOT và E2E percentile |
| [03-serve-and-smoke.png](screenshots/03-serve-and-smoke.png) | Server listen :8080, completion và tokens_predicted_total 0→34 |
| [04-locust-10.png](screenshots/04-locust-10.png) | 31 request, RPS 0,54, P95 22 giây |
| [05-locust-50.png](screenshots/05-locust-50.png) | 44 request, RPS 0,76, P95 52 giây |

Ảnh benchmark và load hiển thị report/log đã lưu của phép đo gốc. Ảnh benchmark
được chụp trước khi cập nhật nhãn review; bảng số liệu giữ nguyên. Smoke trong ảnh
số 3 là lần chạy lại (tokens 0→34), khác log gốc (0→38); không thay số liệu gốc.
