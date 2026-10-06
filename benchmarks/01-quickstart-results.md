# 01 - Measure: latency baseline

Model `Qwen3.5 0.8B` · host `Windows-AMD64` · llama.cpp `b10488`
Settings: `threads=4` `ngl=0` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `Q4_K_M` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| Q4_K_M | 0.50 | 2625 | 347 / 413 | 27.6 / 31.7 | 2083 / 2329 / 2329 | 36.3 |
| UD-Q2_K_XL | 0.39 | 2434 | 395 / 462 | 27.3 / 29.0 | 2105 / 2251 / 2251 | 36.6 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` and `Q4_K_M` decode within 2% of each other here, for 0.11 GB difference on disk.

## Observation

Q2 decode nhanh hơn khoảng 0,8% và nhỏ hơn 0,11 GiB; chưa có lợi ích tốc độ rõ. Đã hỏi cùng câu trên cả hai. Câu dài bị cắt ở 200 token; khi yêu cầu ngắn, cả hai vẫn nhầm goodput với data rate, Q2 còn trả ví dụ sai. Đề xuất giữ Q4, kiểm tra factuality trước sử dụng.

Hai lượt comparison dùng cùng prompt/settings cho từng cặp (temperature=0, seed=42, max_tokens=200). Lượt đầu cả hai finish_reason=length; lượt ngắn finish_reason=stop. Hai cặp câu hỏi không đủ kết luận chất lượng chung do quantization. Smoke trả completion và metrics đúng, nhưng định nghĩa goodput của model sai. RAG cũng bịa tên đầy đủ TTFT/TPOT và trộn prefix caching với disaggregated serving. Giữ nguyên raw output để đánh giá; không sửa câu trả lời nhằm làm đẹp kết quả.

10 prompt/quant; nearest-rank P95 và P99 cùng bằng mẫu lớn nhất ở n=10. Chênh lệch decode <1% chưa đủ chứng minh speedup ổn định. Các quant mixed precision không phải toàn bộ tensor đều đúng 2 hay 4 bit.
