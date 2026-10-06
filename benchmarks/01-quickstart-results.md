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

## Observation ? b?n nh?p c?n review

Q2 decode nhanh h?n kho?ng 0,8% v? nh? h?n 0,11 GiB; ch?a c? l?i ?ch t?c ?? r?. ?? h?i c?ng c?u tr?n c? hai. C?u d?i b? c?t ? 200 token; khi y?u c?u ng?n, c? hai v?n nh?m goodput v?i data rate, Q2 c?n tr? v? d? sai. ?? xu?t gi? Q4, ki?m tra factuality tr??c s? d?ng.

Hai l??t comparison d?ng c?ng prompt/settings cho t?ng c?p (temperature=0, seed=42, max_tokens=200). L??t ??u c? hai finish_reason=length; l??t ng?n finish_reason=stop. M?t c?p c?u h?i kh?ng ?? k?t lu?n ch?t l??ng chung do quantization. Smoke tr? completion v? metrics ??ng, nh?ng ??nh ngh?a goodput c?a model sai. RAG c?ng b?a expansion TTFT/TPOT v? tr?n prefix caching v?i disaggregated serving. Gi? nguy?n output ?? ??nh gi?; kh?ng s?a c?u tr? l?i nh?m l?m ??p k?t qu?.

10 prompt/quant; nearest-rank P95 v? P99 c?ng b?ng m?u l?n nh?t ? n=10. Ch?nh l?ch decode <1% ch?a ?? ch?ng minh speedup ?n ??nh. C?c quant mixed precision kh?ng ph?i to?n b? tensor ??u ??ng 2 hay 4 bit.
