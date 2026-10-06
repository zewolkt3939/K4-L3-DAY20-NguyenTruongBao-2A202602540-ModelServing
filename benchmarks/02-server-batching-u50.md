# 02 - Continuous batching under load (u50)

Host `Windows-AMD64` · `--parallel 4` · 15 samples over
65s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.86 of 4 slots (96%) |
| `requests_processing` | 4 |
| `requests_deferred` | 46 |
| `kv_cache_usage_ratio` | n/a — not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 4431 |

Highest sampled value was **3.86 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.

## Observation ? b?n nh?p c?n review

Peak sampled average busy slots l? 3.86/4 (96.4%), processing ??t 4 v? deferred ??t 46. ??y l? b?ng ch?ng continuous batching v? queueing. Effective concurrency 21.6 t?nh c? th?i gian ch? n?n kh?ng ph?i s? slot ?ang decode; kh?ng c?n b?ng peak 3.86. Gauge n?y l? trung b?nh theo decode step, g?m l?ch s? request t? c?ng server; kh?ng ph?i instantaneous batch width. CSV c? 15 sample; chu k? th?c t? g?m th?i gian scrape c?ng sleep, kh?ng ph?i ch?nh x?c 2 gi?y/sample.
