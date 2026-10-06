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


## Real/stub declaration ? b?n nh?p c?n review

N16 cloud/IaC: stub, localhost. N17: stub, TOY_DOCS trong RAM. N18: stub, danh s?ch Python thay lakehouse. N19: stub, keyword overlap; kh?ng c? embedding/vector index th?t. N20: real, llama-server b10488 tr?n CPU v? 3 query ?? ch?y th?nh c?ng. Stage llm chi?m g?n 100% th?i gian, bao g?m HTTP, queue/prefill/decode; embed=0 kh?ng ??i di?n cho embedding model nhanh. Th? r?t ng?n c?u tr? l?i ho?c CPU?CUDA r?i ?o l?i, ki?m tra ch?t l??ng tr??c khi k?t lu?n c? th? gi?m latency 2?. SYSTEM_PROMPT c? ??nh gi?p gi? common prefix; kh?ng c? ph?p ?o cache-hit ??c l?p trong run n?y.

Hai l??t comparison d?ng c?ng prompt/settings cho t?ng c?p (temperature=0, seed=42, max_tokens=200). L??t ??u c? hai finish_reason=length; l??t ng?n finish_reason=stop. M?t c?p c?u h?i kh?ng ?? k?t lu?n ch?t l??ng chung do quantization. Smoke tr? completion v? metrics ??ng, nh?ng ??nh ngh?a goodput c?a model sai. RAG c?ng b?a expansion TTFT/TPOT v? tr?n prefix caching v?i disaggregated serving. Gi? nguy?n output ?? ??nh gi?; kh?ng s?a c?u tr? l?i nh?m l?m ??p k?t qu?.
