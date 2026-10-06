"""Download the chosen Qwen GGUFs via the mirror documented by this lab.

Writes .part files until the full Content-Length has been received. Re-running
resumes a partial download when the server supports byte ranges.
"""
import http.client
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
import labkit


def download(filename, target=None, url=None):
    target = target or ROOT / "models" / filename
    target.parent.mkdir(exist_ok=True)
    if target.exists():
        print(f"Already present: {filename}", flush=True)
        return
    partial = target.with_name(target.name + ".part")
    url = url or labkit.model_file_url(filename, mirror=True, key="qwen35-0.8b")
    for attempt in range(1, 4):
        offset = partial.stat().st_size if partial.exists() else 0
        headers = {"User-Agent": "day20-lab"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers),
                                        timeout=30) as response:
                resumed = offset and response.status == 206
                content_range = response.headers.get("Content-Range", "")
                match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", content_range)
                if resumed and (not match or int(match[1]) != offset):
                    raise OSError("Server returned an unexpected byte range")
                if not resumed:
                    offset = 0
                total = int(match[3]) if match else offset + int(response.headers.get("Content-Length") or 0)
                print(f"{filename}: downloading from {offset / 1e6:.1f} MB", flush=True)
                done, last = offset, time.monotonic()
                with partial.open("ab" if resumed else "wb") as stream:
                    while chunk := response.read(65536):
                        stream.write(chunk)
                        done += len(chunk)
                        if time.monotonic() - last >= 10:
                            print(f"  {done / 1e6:.1f}/{total / 1e6:.1f} MB", flush=True)
                            last = time.monotonic()
                if not total or done != total:
                    raise OSError(f"Incomplete download: {done}/{total} bytes")
                if target.suffix == ".gguf":
                    with partial.open("rb") as stream:
                        if stream.read(4) != b"GGUF":
                            raise OSError("Downloaded file is not GGUF")
                elif target.suffix == ".zip":
                    import zipfile
                    with zipfile.ZipFile(partial) as archive:
                        if archive.testzip():
                            raise OSError("Runtime archive checksum failed")
                partial.replace(target)
                print(f"Complete: {filename} ({done / 1e6:.1f} MB)", flush=True)
                return
        except (OSError, urllib.error.URLError, http.client.IncompleteRead) as exc:
            print(f"Attempt {attempt}/3 failed: {exc}", flush=True)
    raise RuntimeError(f"Cannot download {filename}; partial data retained for retry")


if __name__ == "__main__":
    if "--runtime-only" in sys.argv:
        name = f"llama-{labkit.LLAMA_CPP_BUILD}-bin-win-cpu-x64.zip"
        target = ROOT / "runtime" / labkit.LLAMA_CPP_BUILD / name
        if target.exists():
            import zipfile
            if not zipfile.is_zipfile(target):
                target.replace(target.with_name(target.name + ".part"))
        download(name, target=target, url=f"https://github.com/ggml-org/llama.cpp/releases/download/{labkit.LLAMA_CPP_BUILD}/{name}")
    else:
        for name in (labkit.primary_file("qwen35-0.8b"), labkit.compare_file("qwen35-0.8b")):
            download(name)
