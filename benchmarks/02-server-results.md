# 02 - Serve: load test + saturation reading

Host `Windows-AMD64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=4` ·
`ngl=0`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 31 | 0.54 | 16000 | 22000 | 23000 | 8.4 | 0.0% |
| 50 | 44 | 0.76 | 29000 | 52000 | 57000 | 21.6 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **1.41x** (28% of linear) |
| P95 latency | **2.36x** |
| Effective concurrency at 50 users | 21.6 vs `--parallel 4` slots (occupancy/slot ratio 5.40) |

**Saturated.** Throughput delivered only 1.41x for 5x the offered load, and effective concurrency (21.6) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.

Throughput moved 1.41x while P95 moved 2.36x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)

## Saturation reading ? b?n nh?p c?n review

10?50 users ch? t?ng RPS 1.41? trong khi P95 t?ng 2.36?. Effective concurrency 21.6 l?n h?n 4 slot; metrics c? deferred t?i 46. Hai ngu?n n?y h? tr? k?t lu?n server b?o h?a v? c? queueing. Kh?ng suy ra to?n b? latency t?ng l? queue time: compute v? workload mix c?ng c? th? thay ??i. Th? gi?i h?n admission/concurrency tr??c ?? b?o v? tail latency; ?o l?i l??ng request b? t? ch?i ?? kh?ng ??nh ??i latency b?ng vi?c che gi?u failures.

SLO minh h?a: E2E P95 ? 30 gi?y (kh?ng ph?i SLO TTFT/TPOT). Run 10 users ??p ?ng; run 50 users kh?ng ??p ?ng. V?i 10 users, max E2E c?a m?i request ho?n t?t <30 gi?y, n?n observed goodput E2E@30s b?ng RPS 0,54. V?i 50 users, CSV percentile kh?ng cho ph?p t?nh ch?nh x?c s? request ??t 30 gi?y; kh?ng suy ra goodput ch?nh x?c t? aggregate RPS. C?n histogram/per-request log cho con s? ??.

Ch? ch?y 60 gi?y/run, v?i 31 v? 44 request ho?n t?t. P95/P99 l? x?p x? Locust, kh?ng ph?i ph?n ph?i ?n ??nh ?? h?i t?. Request c?n ?ang ch? khi test d?ng kh?ng n?m trong completed-request stats; 0 failures kh?ng c? ngh?a m?i request kh?i t?o ?? ho?n t?t. Little?s Law l? ??c l??ng cho m?t c?a s? h?u h?n c? censoring. 5? l? s? users trong closed-loop test, kh?ng ph?i arrival RPS ?o ???c t?ng ch?nh x?c 5?. C? queueing ngay ? 10 users (effective concurrency 8,4 >4); kh?ng x?c ??nh knee ch?nh x?c v? kh?ng c? c?c ?i?m d??i 10.
