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

## Saturation reading

10→50 users chỉ tăng RPS 1.41× trong khi P95 tăng 2.36×. Effective concurrency 21.6 lớn hơn 4 slot; metrics có deferred tới 46. Hai nguồn này hỗ trợ kết luận server bão hòa và có queueing. Không suy ra toàn bộ latency tăng là queue time: compute và workload mix cũng có thể thay đổi. Thử giới hạn admission/concurrency trước để bảo vệ tail latency; đo lại lượng request bị từ chối để không đánh đổi latency bằng việc che giấu failures.

SLO minh họa: E2E P95 ≤ 30 giây (không phải SLO TTFT/TPOT). Run 10 users đáp ứng; run 50 users không đáp ứng. Với 10 users, max E2E của mọi request hoàn tất <30 giây, nên observed goodput E2E@30s bằng RPS 0,54. Với 50 users, CSV percentile không cho phép tính chính xác số request đạt 30 giây; không suy ra goodput chính xác từ aggregate RPS. Cần histogram/per-request log cho con số đó.

Chỉ chạy 60 giây/run, với 31 và 44 request hoàn tất. P95/P99 là xấp xỉ Locust, không phải phân phối ổn định đã hội tụ. Request còn đang chờ khi test dừng không nằm trong completed-request stats; 0 failures không có nghĩa mọi request khởi tạo đã hoàn tất. Little’s Law là ước lượng cho cửa sổ hữu hạn có censoring. 5× là số users trong closed-loop test, không phải arrival RPS đo được tăng chính xác 5×. Có queueing ngay ở 10 users (effective concurrency 8,4 >4); không xác định knee chính xác vì không có các điểm dưới 10.
