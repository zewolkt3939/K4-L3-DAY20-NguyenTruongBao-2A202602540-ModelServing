# Tr?ng th?i b?i Day 20 ? Nguy?n Tr??ng B?o

**Ph?p ?o base track ?? ch?y th?nh c?ng tr?n laptop local.** Ch?a ?? ?i?u ki?n n?p:
c?n 5 screenshot th?t v? ph?n sinh vi?n review. Ch?a push/n?p LMS.

## K?t qu? th?c t?

- Runtime: llama.cpp b10488 CPU prebuilt; ngl=0, threads=4, ctx=2048, parallel=4.
- Hardware: i5-11300H, 4 core/8 lu?ng, RAM 15,7 GiB; GPU RTX 3050 4 GiB ???c
  ph?t hi?n nh?ng kh?ng d?ng trong inference.
- Hai model Qwen ?? t?i ??, ki?m tra GGUF; models/active.json ghi ???ng d?n portable.
- Baseline: 10/10 request th?nh c?ng m?i quant. Decode Q4=36,3, Q2=36,6 tok/s.
- Tune: 1/2/4/8/16 threads; best=4. 1?4: 14,34?34,13 tok/s, 2,38?.
  So v?i default 4 threads, speedup=1,00?; kh?ng nh?m hai baseline n?y.
- Smoke: API tr? completion; tokens_predicted_total 0?38.
- Load: 10/50 users, m?i run 60 gi?y. 31/44 request ho?n t?t; 0 failures trong
  c?c request ho?n t?t. RPS 0,54?0,76 (1,41?); P95 22?52 gi?y (2,36?).
- Metrics l?y ??ng th?i load-50: busy-slots peak 3,86/4, processing=4,
  deferred peak=46, 15 sample. Gi? nguy?n CSV v? di?n gi?i ??ng gauge trung b?nh.
- RAG ch?y h?t 3 query v? in ?? context. Mean llm=6525,5 ms, total=6525,6 ms.
  N16?N19 l? stub; N20 l? real.
- So ch?t l??ng c?ng prompt/settings tr?n hai quant, g?m l??t d?i b? c?t ? 200
  token v? l??t y?u c?u ng?n k?t th?c b?nh th??ng. Raw answers gi? nguy?n.
- REFLECTION v? 5 report ?? ?i?n t? JSON/CSV th?t, c? b?n nh?p nh?n x?t c?n review.
- 4 ki?m tra h?i quy pass, pip check pass, Python compile pass.

## B?n c?n review

Theo docs/RULES.md ?3, sinh vi?n c?n hi?u v? gi?i th?ch ???c ph?n l?p lu?n ?? n?p.
REFLECTION v? nh?n x?t cu?i m?i report ?ang ghi r? l? b?n nh?p c?n review.

1. ??c REFLECTION ?2?5, ??i chi?u c?c b?ng v?i benchmarks/*.json/*.csv.
2. Ch? ? speedup 2,38? l? 1?4 threads, kh?ng ph?i c?i thi?n so v?i default.
3. Hi?u queueing: effective concurrency t?nh c? request ?ang ch?, kh?c v?i s?
   decode slots. Little?s Law ? test 60 gi?y ch? l? ??c l??ng; request c?n pending
   khi test d?ng b? lo?i kh?i completed stats. Kh?ng x?c ??nh knee ch?nh x?c.
4. Review ch?t l??ng: c? hai quant tr? l?i sai goodput trong ph?p h?i t? do.
   RAG c?ng b?a t?n ??y ?? TTFT/TPOT v? l?n prefix cache v?i disaggregation.
   API ch?y ???c kh?ng ch?ng minh c?u tr? l?i ??ng; kh?ng s?a raw output.
5. Ch? gi? nh?n x?t b?n hi?u v? ??ng ?. X?c nh?n N16?N19 v?n stub. Ng?y b?o c?o
   l? 2026-10-06; c?p nh?t ng?y submit th?c t? khi n?p.

## 5 screenshot th?t c?n thi?u

L?y screenshot terminal th?t t? k?t qu? ?? l?u; kh?ng c?n ch?y l?i benchmark
ch? ?? ch?p ?nh. C?c l?nh sau hi?n th? b?ng ch?ng c?a l?n ch?y v?a ho?n t?t:

```powershell
Get-Content benchmarks\logs\01-hardware-probe.txt
Get-Content benchmarks\01-quickstart-results.md
Get-Content benchmarks\logs\04-locust-10.txt -Tail 25
Get-Content benchmarks\logs\05-locust-50.txt -Tail 25
```

Ch?p v? l?u t??ng ?ng:

- submission/screenshots/01-hardware-probe.png
- submission/screenshots/02-bench.png
- submission/screenshots/04-locust-10.png
- submission/screenshots/05-locust-50.png

?nh s? 3 c?n server ?ang listen v? output smoke. M? hai terminal ? root repo:

```powershell
# Terminal 1: gi? ch?y
.\lab.ps1 serve
# Terminal 2
.\lab.ps1 smoke
```

Ch?p c? server v? smoke c? completion + tokens_predicted_total kh?c 0, l?u
submission/screenshots/03-serve-and-smoke.png (ho?c 03a/03b theo README).
D?ng Ctrl+C d?ng server sau khi ch?p. C?c ?nh ph?i r? b?ng s? li?u, crop g?n,
kh?ng c? token/password. Chi ti?t: submission/screenshots/README.md.

## Ki?m tra v? n?p

Sau khi review v? th?m ?nh, commit c?c c?p nh?t, r?i ch?y verify:

```powershell
git add submission benchmarks hardware.json models/active.json
git commit -m "Review report and add real lab screenshots"
.\lab.ps1 verify
```

Verify ph?i exit 0. Sau ?? ki?m tra repo public, push commit v? paste URL v?o LMS
tr??c deadline coach ?p d?ng. Kh?ng force-add models/*.gguf, runtime/, .venv/, .env.
Bonus kh?ng b?t bu?c v? ch?a th?c hi?n.

## Ch?y l?i n?u c?n

```powershell
$env:LAB_MODEL = 'qwen35-0.8b'
.\lab.ps1 run-base
```

Ch?y l?i s? ghi ?? c?c report/JSON v? b?n comparison ??u ti?n; c?n review/?i?n
l?i nh?n x?t v? REFLECTION theo s? m?i. Ch? ch?y l?i khi c? thay ??i ho?c nghi ng?
ph?p ?o, kh?ng s?a tay s? li?u trong b?ng ?? gi? k?t qu? c?.
