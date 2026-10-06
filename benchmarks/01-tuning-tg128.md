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

## Explanation ? b?n nh?p c?n review

Knee ? 4 lu?ng: 34.13 tok/s; 8 lu?ng ??t 33.84, g?n nh? kh?ng t?ng; 16 lu?ng gi?m c?n 25.01. M?y c? 4 core v?t l?, n?n SMT kh?ng b? sung core hay memory channel. Plateau ph? h?p v?i gi?i h?n t?i nguy?n chung; oversubscription t?ng tranh ch?p v? chi ph? scheduling. ??y l? gi?i th?ch ph? h?p s? ?o, ch?a ph?i ch?ng minh memory bandwidth v? kh?ng ?o performance counter. Default 4 lu?ng ?? t?i ?u trong grid n?y; 1?4 l? ph?p so s?nh ki?m so?t, kh?ng ph?i speedup so v?i default.
