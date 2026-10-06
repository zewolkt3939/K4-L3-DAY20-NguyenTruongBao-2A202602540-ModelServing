# Reflection ? Day 20 Lab

> B?n nh?p ???c Codex h? tr? t? s? li?u ?o th?t. Nguy?n Tr??ng B?o c?n review
> c?c nh?n x?t ?2?5 v? gi?i th?ch ???c c? ch? tr??c khi n?p, theo docs/RULES.md ?3.

**H? t?n:** Nguy?n Tr??ng B?o
**MSSV:** 2A202602540
**Cohort:** K4-L3
**Ng?y chu?n b? b?o c?o:** 2026-10-06 (UTC+7). Ch?a n?p LMS; c?p nh?t ng?y submit th?c t? khi n?p.

## 1. Hardware & runtime

- OS: Windows 11 AMD64; Python 3.12.6.
- CPU: Intel Core i5-11300H @3.10 GHz; 4 core physical / 8 logical.
- CPU extensions: ch?a ?o ri?ng; kh?ng suy ra AVX flags t? t?n CPU.
- RAM: 15,7 GiB; hardware probe v? psutil cho c?ng k?t qu?.
- GPU l?p trong m?y: RTX 3050 Laptop 4096 MiB. **Inference th?c t?: CPU, ngl=0**.
- Runtime: llama.cpp b10488; asset llama-b10488-bin-win-cpu-x64.zip.
- Model: Qwen3.5 0.8B; LAB_MODEL=qwen35-0.8b; Q4_K_M + UD-Q2_K_XL.
- M?i tr??ng: laptop local. Settings chung: threads=4, ctx=2048, parallel=4,
  continuous batching v? metrics b?t, reasoning=off. Bench max_tokens=64;
  load short/long max_tokens=48/96; pipeline max_tokens=200.

Setup story: CIM b? Access denied l?m probe c? ??c sai RAM. ?? d?ng registry/Windows
API ?? ?o ??ng. CUDA download timeout n?n d?ng CPU prebuilt; CPU ZIP ???c t?i ti?p v?
ki?m tra checksum ZIP th?nh c?ng. Hai GGUF Qwen t?i qua mirror, ki?m tra magic GGUF
v? ?? dung l??ng. Runtime/model ho?n ch?nh r?i m?i t?o manifest v? ch?y inference.

## 2. ?o l??ng

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| Q4_K_M | 0.50 | 2625 | 347 / 413 | 27.6 / 31.7 | 2083 / 2329 / 2329 | 36.3 |
| UD-Q2_K_XL | 0.39 | 2434 | 395 / 462 | 27.3 / 29.0 | 2105 / 2251 / 2251 | 36.6 |

**Quan s?t:** Q2 decode nhanh h?n kho?ng 0,8% v? nh? h?n 0,11 GiB; ch?a c? l?i ?ch t?c ?? r?. ?? h?i c?ng c?u tr?n c? hai. C?u d?i b? c?t ? 200 token; khi y?u c?u ng?n, c? hai v?n nh?m goodput v?i data rate, Q2 c?n tr? v? d? sai. ?? xu?t gi? Q4, ki?m tra factuality tr??c s? d?ng.

Warm-up b? lo?i; m?i quant c? 10 request th?nh c?ng. TTFT ?o ? client t?i content
??u ti?n, g?m HTTP/scheduling/prefill; TPOT d?ng output token count c?a server.
P95=P99 ? n=10 theo nearest-rank. Ch?nh l?ch t?c ?? 1.008? ch?a v??t nhi?u
c?a m?t l?n ch?y. Hai l??t ch?t l??ng l?u nguy?n trong 01-quality-comparison.json.

## 3. Serving under load

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 31 | 0.54 | 16000 | 22000 | 23000 | 8.4 | 0.0% |
| 50 | 44 | 0.76 | 29000 | 52000 | 57000 | 21.6 | 0.0% |

- Users t?ng 5?; throughput t?ng 1.41?; P95 t?ng 2.36?.
- Effective concurrency ? 50 users: 21.6 so v?i 4 slots.
- Peak sampled busy slots: 3.86/4; processing=4; deferred peak=46.
- Smoke: tokens_predicted_total t?ng 0?38; /v1/chat/completions tr? completion th?t.

**Saturation reading:** RPS t?ng 1.41?, P95 t?ng 2.36?; deferred t?i
46, effective concurrency 21.6>4. Server c? queueing; kh?ng ??nh v?
???c knee ch?nh x?c v? ch? ?o 10/50 users. ?? xu?t gi?i h?n admission/concurrency
?? b?o v? SLO E2E P95?30 gi?y, ?o c? rejected requests. Kh?ng t?ng threads v?
thread sweep ?? ??t ??nh ? 4; t?ng parallel c? th? k?o d?i decode/KV pressure.

SLO minh h?a: E2E P95 ? 30 gi?y (kh?ng ph?i SLO TTFT/TPOT). Run 10 users ??p ?ng; run 50 users kh?ng ??p ?ng. V?i 10 users, max E2E c?a m?i request ho?n t?t <30 gi?y, n?n observed goodput E2E@30s b?ng RPS 0,54. V?i 50 users, CSV percentile kh?ng cho ph?p t?nh ch?nh x?c s? request ??t 30 gi?y; kh?ng suy ra goodput ch?nh x?c t? aggregate RPS. C?n histogram/per-request log cho con s? ??.

Ch? ch?y 60 gi?y/run, v?i 31 v? 44 request ho?n t?t. P95/P99 l? x?p x? Locust, kh?ng ph?i ph?n ph?i ?n ??nh ?? h?i t?. Request c?n ?ang ch? khi test d?ng kh?ng n?m trong completed-request stats; 0 failures kh?ng c? ngh?a m?i request kh?i t?o ?? ho?n t?t. Little?s Law l? ??c l??ng cho m?t c?a s? h?u h?n c? censoring. 5? l? s? users trong closed-loop test, kh?ng ph?i arrival RPS ?o ???c t?ng ch?nh x?c 5?. C? queueing ngay ? 10 users (effective concurrency 8,4 >4); kh?ng x?c ??nh knee ch?nh x?c v? kh?ng c? c?c ?i?m d??i 10.

## 4. Integration

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | localhost, kh?ng k?t n?i cloud/IaC | stub |
| N17 Data pipeline | TOY_DOCS trong b? nh? | stub |
| N18 Lakehouse | Python list thay lakehouse | stub |
| N19 Vector + features | keyword overlap, kh?ng embedding server | stub |
| N20 Serving | llama-server b10488, CPU | real; ch?y h?t 3 query |

Mean c?a 3 query:

- embed: 0.0 ms (kh?ng g?i embedding model).
- retrieve: 0.1 ms.
- llm: 6525.5 ms.
- total: 6525.6 ms.
- Stage l?n nh?t: llm, 99.998% total (report l?m tr?n 100%).

**Reflection:** LLM chi?m g?n to?n b? latency; stage n?y g?m HTTP, scheduling,
prefill v? decode. ?? xu?t r?t ng?n output r?i ?o l?i ch?t l??ng; CUDA l? m?t
experiment ti?p theo. Kh?ng th? kh?ng ??nh gi?m latency 2? tr??c khi ?o.
SYSTEM_PROMPT gi? nguy?n t?ng byte; ch?a ?o ??c l?p hi?u qu? prefix cache.

Hai l??t comparison d?ng c?ng prompt/settings cho t?ng c?p (temperature=0, seed=42, max_tokens=200). L??t ??u c? hai finish_reason=length; l??t ng?n finish_reason=stop. M?t c?p c?u h?i kh?ng ?? k?t lu?n ch?t l??ng chung do quantization. Smoke tr? completion v? metrics ??ng, nh?ng ??nh ngh?a goodput c?a model sai. RAG c?ng b?a expansion TTFT/TPOT v? tr?n prefix caching v?i disaggregated serving. Gi? nguy?n output ?? ??nh gi?; kh?ng s?a c?u tr? l?i nh?m l?m ??p k?t qu?.

## 5. The single change that mattered most

**Change trong sweep ki?m so?t:** t?ng -t t? 1 l?n 4, tr?n c?ng Q4_K_M, CPU,
llama-bench tg128, 2 repetitions m?i ?i?m.

```text
before:  14.34 tok/s (-t 1)
after:   34.13 tok/s (-t 4)
speedup: 2.38?
```

M?t lu?ng ch?a t?n d?ng ?? 4 core v?t l? ?? x? l? c?c ph?p to?n decode. Khi t?ng
l?n 4 lu?ng, c?ng vi?c ???c chia cho nhi?u core; throughput t?ng 2.38?, ch?a
??t tuy?n t?nh 4? v? v?n c? ph?n tu?n t? v? t?i nguy?n b? nh? d?ng chung. Knee
n?m ? 4 lu?ng: 8 lu?ng ??t 33.84 tok/s so v?i 34.13 ? 4 lu?ng.
SMT chia s? execution resources; th?m lu?ng kh?ng b? sung memory channel.

16 lu?ng ch? ??t 25.01 tok/s, ph? h?p v?i oversubscription, scheduling v?
tranh ch?p t?i nguy?n. Kh?ng ?o bandwidth/performance counters n?n ??y l? c? ch?
ph? h?p d? li?u, ch?a ch?ng minh bandwidth l? nguy?n nh?n duy nh?t. Default c?a
lab ?? l? 4 lu?ng: speedup so v?i default l? 1,00?. 2.38? l? so v?i c?u h?nh
1 lu?ng th?c s? ?? ?o, kh?ng ph?i tuy?n b? t?i ?u default th?m 2.38?.

## 6. Bonus

Kh?ng l?m bonus; ?u ti?n ho?n t?t base v? review ch?t l??ng.

## 7. ?i?m c?n review

Hai quant g?n ngang t?c ?? nh?ng output c? factual errors; ch?y API th?nh c?ng
kh?ng ??ng ngh?a c?u tr? l?i ??ng. C?n review raw answers tr??c khi ch?p nh?n k?t
lu?n ch?t l??ng. N16?N19 v?n stub, kh?ng ph?i stack th?t c?a c?c ng?y tr??c.

## 8. Self-check tr??c khi push

- [x] Hardware, manifest, baseline, tune, hai load CSV, metrics v? pipeline ?? t?o.
- [x] C?c s? trong b?o c?o l?y t? JSON/CSV; gi? nguy?n b?ng generated report.
- [x] Khai b?o CPU inference, c?c stub v? vi?c d?ng AI.
- [ ] Sinh vi?n review l?p lu?n v? ch?t l??ng c?u tr? l?i.
- [ ] 5 screenshot th?t ? submission/screenshots.
- [ ] Commit b?ng ch?ng v? .\lab.ps1 verify exit 0.
- [ ] Ki?m tra repo public, push v? paste URL v?o LMS theo deadline coach.

## 9. Khai b?o s? d?ng AI

D?ng OpenAI Codex ?? ??c ??/rubric, s?a l?i Windows, h? tr? setup, ch?y benchmark,
load test/metrics v? pipeline, t?ng h?p s? li?u ?o th?t v? so?n b?n nh?p nh?n x?t.
Sinh vi?n ph?i review v? hi?u ?2?5 tr??c khi n?p; kh?ng d?ng s? li?u ho?c screenshot
gi?. Ch?a d?ng cloud, ch?a push hay n?p LMS trong phi?n n?y.
