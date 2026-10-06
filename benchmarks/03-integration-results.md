# 03 - Integrate: RAG pipeline run

Host `Windows-AMD64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.1 | 7879.1 | 7879.3 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.0 | 6117.7 | 6117.7 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.1 | 5579.6 | 5579.7 |

Mean per stage (ms): embed **0.0** · retrieve **0.1** ·
llm **6525.5** · total **6525.6**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Based on the provided context, **Goodput is more useful than raw throughput** because it focuses on the specific metrics that define a system's performance at its limits.

While raw throughput measures total requests per second (which can be artificially inflated by ignoring SLOs), Goodput specifically counts only the requests that met the Target Time-to-Fill (TTFT) and Target Time-to-Poll (TPOT)

**What problem does PagedAttention actually solve?**

> PagedAttention solves the problem of **internal fragmentation in GPU memory** caused by storing key-value pairs (KV cache) in non-contiguous pages.

By organizing the KV cache into separate pages rather than a single contiguous block, it eliminates the wasted space that would otherwise be consumed by the internal fragmentation of the contiguous memory layout. This allows the engine to utilize more

**When does splitting prefill and decode help?**

> Based on the context provided, splitting prefill and decode helps when **prefill is compute-bound and decode is memory-bandwidth-bound**.

This is achieved by having the engine skip prefill entirely if a shared prefix is used in a **RadixAttention** structure. This optimization allows the engine to skip the expensive prefill step entirely, thereby improving performance in scenarios where the memor


## Real/stub declaration

N16 cloud/IaC: stub, localhost. N17: stub, TOY_DOCS trong RAM. N18: stub, danh sách Python thay lakehouse. N19: stub, keyword overlap; không có embedding/vector index thật. N20: real, llama-server b10488 trên CPU và 3 query đã chạy thành công. Stage llm chiếm gần 100% thời gian, bao gồm HTTP, queue/prefill/decode; embed=0 không đại diện cho embedding model nhanh. Thử rút ngắn câu trả lời hoặc CPU→CUDA rồi đo lại, kiểm tra chất lượng trước khi kết luận có thể giảm latency 2×. SYSTEM_PROMPT cố định giúp giữ common prefix; không có phép đo cache-hit độc lập trong run này.

Hai lượt comparison dùng cùng prompt/settings cho từng cặp (temperature=0, seed=42, max_tokens=200). Lượt đầu cả hai finish_reason=length; lượt ngắn finish_reason=stop. Hai cặp câu hỏi không đủ kết luận chất lượng chung do quantization. Smoke trả completion và metrics đúng, nhưng định nghĩa goodput của model sai. RAG cũng bịa tên đầy đủ TTFT/TPOT và trộn prefix caching với disaggregated serving. Giữ nguyên raw output để đánh giá; không sửa câu trả lời nhằm làm đẹp kết quả.
