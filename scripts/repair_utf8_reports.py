"""Restore Vietnamese prose damaged by a Windows PowerShell stdin encoding.

Read measurements from JSON; preserve generated report tables and raw outputs.
This source is UTF-8 and runs directly, without piping Unicode through a shell.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "benchmarks"


def read(name):
    return json.loads((B / name).read_text(encoding="utf-8"))


def write(path, text):
    path.write_text(text.strip() + "\n", encoding="utf-8")


def table(name):
    lines = (B / name).read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("|"))
    end = start
    while end < len(lines) and lines[end].startswith("|"):
        end += 1
    return "\n".join(lines[start:end])


def main():
    baseline = read("01-quickstart-results.json")
    tune = read("01-tuning-tg128.json")
    load = read("02-server-results.json")
    pipeline = read("03-integration-results.json")
    rates = {r["threads"]: r["tok_s"] for r in tune["rows"]}
    gain = rates[4] / rates[1]
    low, high = load["runs"]
    ratio = high["rps"] / low["rps"]
    p95_ratio = high["p95_ms"] / low["p95_ms"]
    conc = high["rps"] * high["avg_ms"] / 1000
    means = pipeline["mean_ms"]

    quality = (
        "Q2 decode nhanh hơn khoảng 0,8% và nhỏ hơn 0,11 GiB; chưa có lợi ích tốc độ rõ. "
        "Đã hỏi cùng câu trên cả hai. Câu dài bị cắt ở 200 token; khi yêu cầu ngắn, "
        "cả hai vẫn nhầm goodput với data rate, Q2 còn trả ví dụ sai. "
        "Đề xuất giữ Q4, kiểm tra factuality trước sử dụng."
    )
    quality_limits = (
        "Hai lượt comparison dùng cùng prompt/settings cho từng cặp "
        "(temperature=0, seed=42, max_tokens=200). Lượt đầu cả hai finish_reason=length; "
        "lượt ngắn finish_reason=stop. Hai cặp câu hỏi không đủ kết luận chất lượng chung "
        "do quantization. Smoke trả completion và metrics đúng, nhưng định nghĩa goodput "
        "của model sai. RAG cũng bịa tên đầy đủ TTFT/TPOT và trộn prefix caching với "
        "disaggregated serving. Giữ nguyên raw output để đánh giá; không sửa câu trả lời "
        "nhằm làm đẹp kết quả."
    )
    tuning = (
        f"Knee ở 4 luồng: {rates[4]:.2f} tok/s; 8 luồng đạt {rates[8]:.2f}, gần như "
        f"không tăng; 16 luồng giảm còn {rates[16]:.2f}. Máy có 4 core vật lý, nên SMT "
        "không bổ sung core hay memory channel. Plateau phù hợp với giới hạn tài nguyên "
        "chung; oversubscription tăng tranh chấp và chi phí scheduling. Đây là giải thích "
        "phù hợp số đo, chưa phải chứng minh memory bandwidth vì không đo performance "
        "counter. Default 4 luồng đã tối ưu trong grid này; 1→4 là phép so sánh kiểm soát, "
        "không phải speedup so với default."
    )
    saturation = (
        f"10→50 users chỉ tăng RPS {ratio:.2f}× trong khi P95 tăng {p95_ratio:.2f}×. "
        f"Effective concurrency {conc:.1f} lớn hơn 4 slot; metrics có deferred tới 46. "
        "Hai nguồn này hỗ trợ kết luận server bão hòa và có queueing. Không suy ra toàn "
        "bộ latency tăng là queue time: compute và workload mix cũng có thể thay đổi. "
        "Thử giới hạn admission/concurrency trước để bảo vệ tail latency; đo lại lượng "
        "request bị từ chối để không đánh đổi latency bằng việc che giấu failures."
    )
    slo = (
        "SLO minh họa: E2E P95 ≤ 30 giây (không phải SLO TTFT/TPOT). Run 10 users "
        "đáp ứng; run 50 users không đáp ứng. Với 10 users, max E2E của mọi request hoàn "
        "tất <30 giây, nên observed goodput E2E@30s bằng RPS 0,54. Với 50 users, CSV "
        "percentile không cho phép tính chính xác số request đạt 30 giây; không suy ra "
        "goodput chính xác từ aggregate RPS. Cần histogram/per-request log cho con số đó."
    )
    limits = (
        "Chỉ chạy 60 giây/run, với 31 và 44 request hoàn tất. P95/P99 là xấp xỉ Locust, "
        "không phải phân phối ổn định đã hội tụ. Request còn đang chờ khi test dừng không "
        "nằm trong completed-request stats; 0 failures không có nghĩa mọi request khởi "
        "tạo đã hoàn tất. Little’s Law là ước lượng cho cửa sổ hữu hạn có censoring. "
        "5× là số users trong closed-loop test, không phải arrival RPS đo được tăng "
        "chính xác 5×. Có queueing ngay ở 10 users (effective concurrency 8,4 >4); "
        "không xác định knee chính xác vì không có các điểm dưới 10."
    )
    batching = (
        f"Peak sampled average busy slots là 3,86/4 (96,5%), processing đạt 4 và "
        f"deferred đạt 46. Đây là bằng chứng continuous batching và queueing. Effective "
        f"concurrency {conc:.1f} tính cả thời gian chờ nên không phải số slot đang decode; "
        "không cần bằng peak 3,86. Gauge này là trung bình theo decode step, gồm lịch sử "
        "request từ cùng server; không phải instantaneous batch width. CSV có 15 sample; "
        "chu kỳ thực tế gồm thời gian scrape cộng sleep, không phải chính xác 2 giây/sample."
    )
    integration = (
        "N16 cloud/IaC: stub, localhost. N17: stub, TOY_DOCS trong RAM. N18: stub, "
        "danh sách Python thay lakehouse. N19: stub, keyword overlap; không có "
        "embedding/vector index thật. N20: real, llama-server b10488 trên CPU và 3 query "
        "đã chạy thành công. Stage llm chiếm gần 100% thời gian, bao gồm HTTP, "
        "queue/prefill/decode; embed=0 không đại diện cho embedding model nhanh. "
        "Thử rút ngắn câu trả lời hoặc CPU→CUDA rồi đo lại, kiểm tra chất lượng trước "
        "khi kết luận có thể giảm latency 2×. SYSTEM_PROMPT cố định giúp giữ common "
        "prefix; không có phép đo cache-hit độc lập trong run này."
    )
    observations = [
        ("01-quickstart-results.md", "Observation", quality + "\n\n" + quality_limits
         + "\n\n10 prompt/quant; nearest-rank P95 và P99 cùng bằng mẫu lớn nhất ở n=10. "
           "Chênh lệch decode <1% chưa đủ chứng minh speedup ổn định. Các quant mixed "
           "precision không phải toàn bộ tensor đều đúng 2 hay 4 bit."),
        ("01-tuning-tg128.md", "Explanation", tuning),
        ("02-server-results.md", "Saturation reading", saturation + "\n\n" + slo + "\n\n" + limits),
        ("02-server-batching-u50.md", "Observation", batching),
        ("03-integration-results.md", "Real/stub declaration", integration + "\n\n" + quality_limits),
    ]
    for name, heading, body in observations:
        path = B / name
        text = path.read_text(encoding="utf-8")
        marker = "\n## " + heading
        assert marker in text, name
        prefix = text.split(marker, 1)[0]
        write(path, prefix + marker + " — bản nháp cần review\n\n" + body)

    reflection = f"""# Reflection — Day 20 Lab

> Bản nháp được Codex hỗ trợ từ số liệu đo thật. Nguyễn Trường Bảo cần review
> các nhận xét §2–5 và giải thích được cơ chế trước khi nộp, theo docs/RULES.md §3.

- **Họ tên:** Nguyễn Trường Bảo
- **MSSV:** 2A202602540
- **Cohort:** K4-L3
- **Ngày chuẩn bị báo cáo:** 2026-10-06 (UTC+7). Chưa nộp LMS; cập nhật ngày submit thực tế khi nộp.

## 1. Hardware & runtime

- OS: Windows 11 AMD64; Python 3.12.6.
- CPU: Intel Core i5-11300H @3.10 GHz; 4 core physical / 8 logical.
- CPU extensions: chưa đo riêng; không suy ra AVX flags từ tên CPU.
- RAM: 15,7 GiB; hardware probe và psutil cho cùng kết quả.
- GPU lắp trong máy: RTX 3050 Laptop 4096 MiB. **Inference thực tế: CPU, ngl=0**.
- Runtime: llama.cpp b10488; asset llama-b10488-bin-win-cpu-x64.zip.
- Model: Qwen3.5 0.8B; LAB_MODEL=qwen35-0.8b; Q4_K_M + UD-Q2_K_XL.
- Môi trường: laptop local. Settings chung: threads=4, ctx=2048, parallel=4,
  continuous batching và metrics bật, reasoning=off. Bench max_tokens=64;
  load short/long max_tokens=48/96; pipeline max_tokens=200.

Setup story: CIM bị Access denied làm probe cũ đọc sai RAM. Đã dùng registry/Windows
API để đo đúng. CUDA download timeout nên dùng CPU prebuilt; CPU ZIP được tải tiếp và
kiểm tra checksum ZIP thành công. Hai GGUF Qwen tải qua mirror, kiểm tra magic GGUF
và đủ dung lượng. Runtime/model hoàn chỉnh rồi mới tạo manifest và chạy inference.

## 2. Đo lường

{table('01-quickstart-results.md')}

**Quan sát:** {quality}

Warm-up bị loại; mỗi quant có 10 request thành công. TTFT đo ở client tới content
đầu tiên, gồm HTTP/scheduling/prefill; TPOT dùng output token count của server.
P95=P99 ở n=10 theo nearest-rank. Chênh lệch tốc độ
{baseline['compare']['decode_tok_s']/baseline['primary']['decode_tok_s']:.3f}× chưa vượt nhiễu
của một lần chạy. Hai lượt chất lượng lưu nguyên trong 01-quality-comparison.json.

## 3. Serving under load

{table('02-server-results.md')}

- Users tăng 5×; throughput tăng {ratio:.2f}×; P95 tăng {p95_ratio:.2f}×.
- Effective concurrency ở 50 users: {conc:.1f} so với 4 slots.
- Peak sampled busy slots: 3,86/4; processing=4; deferred peak=46.
- Smoke: tokens_predicted_total tăng 0→38; /v1/chat/completions trả completion thật.

**Saturation reading:** RPS tăng {ratio:.2f}×, P95 tăng {p95_ratio:.2f}×; deferred tới
46, effective concurrency {conc:.1f}>4. Server có queueing; không định vị được knee
chính xác vì chỉ đo 10/50 users. Đề xuất giới hạn admission/concurrency để bảo vệ
SLO E2E P95≤30 giây, đo cả rejected requests. Không tăng threads vì thread sweep
đã đạt đỉnh ở 4; tăng parallel có thể kéo dài decode/KV pressure.

{slo}

{limits}

## 4. Integration

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | localhost, không kết nối cloud/IaC | stub |
| N17 Data pipeline | TOY_DOCS trong bộ nhớ | stub |
| N18 Lakehouse | Python list thay lakehouse | stub |
| N19 Vector + features | keyword overlap, không embedding server | stub |
| N20 Serving | llama-server b10488, CPU | real; chạy hết 3 query |

Mean của 3 query:

- embed: {means['embed']:.1f} ms (không gọi embedding model).
- retrieve: {means['retrieve']:.1f} ms.
- llm: {means['llm']:.1f} ms.
- total: {means['total']:.1f} ms.
- Stage lớn nhất: llm, {100*means['llm']/means['total']:.3f}% total (report làm tròn 100%).

**Reflection:** LLM chiếm gần toàn bộ latency; stage này gồm HTTP, scheduling,
prefill và decode. Đề xuất rút ngắn output rồi đo lại chất lượng; CUDA là một
experiment tiếp theo. Không thể khẳng định giảm latency 2× trước khi đo.
SYSTEM_PROMPT giữ nguyên từng byte; chưa đo độc lập hiệu quả prefix cache.

{quality_limits}

## 5. The single change that mattered most

**Change trong sweep kiểm soát:** tăng -t từ 1 lên 4, trên cùng Q4_K_M, CPU,
llama-bench tg128, 2 repetitions mỗi điểm.

```text
before:  {rates[1]:.2f} tok/s (-t 1)
after:   {rates[4]:.2f} tok/s (-t 4)
speedup: {gain:.2f}×
```

Một luồng chưa tận dụng đủ 4 core vật lý để xử lý các phép toán decode. Khi tăng
lên 4 luồng, công việc được chia cho nhiều core; throughput tăng {gain:.2f}×, chưa
đạt tuyến tính 4× vì vẫn có phần tuần tự và tài nguyên bộ nhớ dùng chung. Knee
nằm ở 4 luồng: 8 luồng đạt {rates[8]:.2f} tok/s so với {rates[4]:.2f} ở 4 luồng.
SMT chia sẻ execution resources; thêm luồng không bổ sung memory channel.

16 luồng chỉ đạt {rates[16]:.2f} tok/s, phù hợp với oversubscription, scheduling và
tranh chấp tài nguyên. Không đo bandwidth/performance counters nên đây là cơ chế
phù hợp dữ liệu, chưa chứng minh bandwidth là nguyên nhân duy nhất. Default của
lab đã là 4 luồng: speedup so với default là 1,00×. {gain:.2f}× là so với cấu hình
1 luồng thực sự đã đo, không phải tuyên bố tối ưu default thêm {gain:.2f}×.

## 6. Bonus

Không làm bonus; ưu tiên hoàn tất base và review chất lượng.

## 7. Điểm cần review

Hai quant gần ngang tốc độ nhưng output có factual errors; chạy API thành công
không đồng nghĩa câu trả lời đúng. Cần review raw answers trước khi chấp nhận kết
luận chất lượng. N16–N19 vẫn stub, không phải stack thật của các ngày trước.

## 8. Self-check trước khi push

- [x] Hardware, manifest, baseline, tune, hai load CSV, metrics và pipeline đã tạo.
- [x] Các số trong báo cáo lấy từ JSON/CSV; giữ nguyên bảng generated report.
- [x] Khai báo CPU inference, các stub và việc dùng AI.
- [ ] Sinh viên review lập luận và chất lượng câu trả lời.
- [ ] 5 screenshot thật ở submission/screenshots.
- [ ] Commit bằng chứng và .\\lab.ps1 verify exit 0.
- [ ] Kiểm tra repo public, push và paste URL vào LMS theo deadline coach.

## 9. Khai báo sử dụng AI

Dùng OpenAI Codex để đọc đề/rubric, sửa lỗi Windows, hỗ trợ setup, chạy benchmark,
load test/metrics và pipeline, tổng hợp số liệu đo thật và soạn bản nháp nhận xét.
Sinh viên phải review và hiểu §2–5 trước khi nộp; không dùng số liệu hoặc screenshot
giả. Chưa dùng cloud, chưa push hay nộp LMS trong phiên này.
"""
    write(ROOT / "submission/REFLECTION.md", reflection)

    status = """# Trạng thái bài Day 20 — Nguyễn Trường Bảo

**Phép đo base track đã chạy thành công trên laptop local.** Chưa đủ điều kiện nộp:
còn 5 screenshot thật và phần sinh viên review. Kết quả đã commit local ở `6b99d7e`;
chưa push/nộp LMS. Bản sửa encoding cần commit bổ sung.

## Kết quả thực tế

- Runtime: llama.cpp b10488 CPU prebuilt; ngl=0, threads=4, ctx=2048, parallel=4.
- Hardware: i5-11300H, 4 core/8 luồng, RAM 15,7 GiB; GPU RTX 3050 4 GiB được
  phát hiện nhưng không dùng trong inference.
- Hai model Qwen đã tải đủ, kiểm tra GGUF; models/active.json ghi đường dẫn portable.
- Baseline: 10/10 request thành công mỗi quant. Decode Q4=36,3, Q2=36,6 tok/s.
- Tune: 1/2/4/8/16 threads; best=4. 1→4: 14,34→34,13 tok/s, 2,38×.
  So với default 4 threads, speedup=1,00×; không nhầm hai baseline này.
- Smoke: API trả completion; tokens_predicted_total 0→38.
- Load: 10/50 users, mỗi run 60 giây. 31/44 request hoàn tất; 0 failures trong
  các request hoàn tất. RPS 0,54→0,76 (1,41×); P95 22→52 giây (2,36×).
- Metrics lấy đồng thời load-50: busy-slots peak 3,86/4, processing=4,
  deferred peak=46, 15 sample. Giữ nguyên CSV và diễn giải đúng gauge trung bình.
- RAG chạy hết 3 query và in đủ context. Mean llm=6525,5 ms, total=6525,6 ms.
  N16–N19 là stub; N20 là real.
- So chất lượng cùng prompt/settings trên hai quant, gồm lượt dài bị cắt ở 200
  token và lượt yêu cầu ngắn kết thúc bình thường. Raw answers giữ nguyên.
- REFLECTION và 5 report đã điền từ JSON/CSV thật, có bản nháp nhận xét cần review.
- 4 kiểm tra hồi quy pass, pip check pass, Python compile pass.

## Bạn cần review

Theo docs/RULES.md §3, sinh viên cần hiểu và giải thích được phần lập luận đã nộp.
REFLECTION và nhận xét cuối mỗi report đang ghi rõ là bản nháp cần review.

1. Đọc REFLECTION §2–5, đối chiếu các bảng với benchmarks/*.json/*.csv.
2. Chú ý speedup 2,38× là 1→4 threads, không phải cải thiện so với default.
3. Hiểu queueing: effective concurrency tính cả request đang chờ, khác với số
   decode slots. Little’s Law ở test 60 giây chỉ là ước lượng; request còn pending
   khi test dừng bị loại khỏi completed stats. Không xác định knee chính xác.
4. Review chất lượng: cả hai quant trả lời sai goodput trong phép hỏi tự do.
   RAG cũng bịa tên đầy đủ TTFT/TPOT và lẫn prefix cache với disaggregation.
   API chạy được không chứng minh câu trả lời đúng; không sửa raw output.
5. Chỉ giữ nhận xét bạn hiểu và đồng ý. Xác nhận N16–N19 vẫn stub. Ngày báo cáo
   là 2026-10-06; cập nhật ngày submit thực tế khi nộp.

## 5 screenshot thật còn thiếu

Lấy screenshot terminal thật từ kết quả đã lưu; không cần chạy lại benchmark
chỉ để chụp ảnh. Các lệnh sau hiển thị bằng chứng của lần chạy vừa hoàn tất:

```powershell
Get-Content -Encoding UTF8 benchmarks\\logs\\01-hardware-probe.txt
Get-Content -Encoding UTF8 benchmarks\\01-quickstart-results.md
Get-Content -Encoding UTF8 benchmarks\\logs\\04-locust-10.txt -Tail 25
Get-Content -Encoding UTF8 benchmarks\\logs\\05-locust-50.txt -Tail 25
```

Chụp và lưu tương ứng:

- submission/screenshots/01-hardware-probe.png
- submission/screenshots/02-bench.png
- submission/screenshots/04-locust-10.png
- submission/screenshots/05-locust-50.png

Ảnh số 3 cần server đang listen và output smoke. Mở hai terminal ở root repo:

```powershell
# Terminal 1: giữ chạy
.\\lab.ps1 serve
# Terminal 2
.\\lab.ps1 smoke
```

Chụp cả server và smoke có completion + tokens_predicted_total khác 0, lưu
submission/screenshots/03-serve-and-smoke.png (hoặc 03a/03b theo README).
Dùng Ctrl+C dừng server sau khi chụp. Các ảnh phải rõ bảng số liệu, crop gọn,
không có token/password. Chi tiết: submission/screenshots/README.md.

## Kiểm tra và nộp

Sau khi review và thêm ảnh, commit các cập nhật, rồi chạy verify:

```powershell
git add submission benchmarks hardware.json models/active.json scripts/repair_utf8_reports.py
git commit -m "Review report, fix encoding and add real lab screenshots"
.\\lab.ps1 verify
```

Verify phải exit 0. Sau đó kiểm tra repo public, push commit và paste URL vào LMS
trước deadline coach áp dụng. Không force-add models/*.gguf, runtime/, .venv/, .env.
Bonus không bắt buộc và chưa thực hiện.

## Chạy lại nếu cần

```powershell
$env:LAB_MODEL = 'qwen35-0.8b'
.\\lab.ps1 run-base
```

Chạy lại sẽ ghi đè các report/JSON và bản comparison đầu tiên; cần review/điền
lại nhận xét và REFLECTION theo số mới. Chỉ chạy lại khi có thay đổi hoặc nghi ngờ
phép đo, không sửa tay số liệu trong bảng để giữ kết quả cũ.
"""
    write(ROOT / "submission/STATUS.md", status)
    print("Restored STATUS, REFLECTION and five report observations as UTF-8.")


if __name__ == "__main__":
    main()
