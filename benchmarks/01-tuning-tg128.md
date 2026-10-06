# 01 - Tune: thread-count sweep

Model `Qwen3.5-0.8B-Q4_K_M.gguf` · host `Windows-AMD64` · llama.cpp `b10488`
CPU: **4 physical · 8 logical** cores · `ngl=0` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 14.3 | 42% |
| 2 | 26.3 | 77% |
| 4 | 34.1 | 100% |
| 8 | 33.8 | 99% |
| 16 | 25.0 | 73% |

**Best**: `-t 4` at 34.1 tok/s
**Slowest tested**: `-t 1` at 14.3 tok/s (2.38x spread)
**Against the physical-core default** (`-t 4`, 34.1 tok/s): 1.00x

Use this in your run:

```bash
LAB_N_THREADS=4 make bench
```

## Explanation

Knee ở 4 luồng: 34.13 tok/s; 8 luồng đạt 33.84, gần như không tăng; 16 luồng giảm còn 25.01. Máy có 4 core vật lý, nên SMT không bổ sung core hay memory channel. Plateau phù hợp với giới hạn tài nguyên chung; oversubscription tăng tranh chấp và chi phí scheduling. Đây là giải thích phù hợp số đo, chưa phải chứng minh memory bandwidth vì không đo performance counter. Default 4 luồng đã tối ưu trong grid này; 1→4 là phép so sánh kiểm soát, không phải speedup so với default.
