"""Regression checks for Windows hardware probing and submission paths."""
import importlib.util
import pathlib
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify = load("verify", "scripts/verify.py")
probe = load("probe", "labs/00-setup/detect-hardware.py")


class Regressions(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "Windows PowerShell 5.1")
    def test_windows_runner_parses(self):
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(ROOT / "lab.ps1"), "help"],
            capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertIn(b"run-base", result.stdout)

    def test_git_paths_use_forward_slashes(self):
        with patch.object(verify, "TRACKED", {"submission/REFLECTION.md"}):
            self.assertTrue(verify.is_committed(ROOT / "submission/REFLECTION.md"))
            self.assertFalse(verify.is_committed(ROOT / "submission/missing.md"))

    def test_reflection_utf8(self):
        # Read the actual Vietnamese template with the same explicit encoding
        # used by the verifier; Windows' default encoding must not affect this.
        text = (ROOT / "submission/REFLECTION.md").read_text(encoding="utf-8")
        self.assertIn("## 1.", text)

    @unittest.skipUnless(sys.platform == "win32", "Windows native APIs")
    def test_native_probe_does_not_need_cim(self):
        with patch.object(probe, "run", return_value=(1, "Access denied 0x80041003")):
            cpu = probe.detect_cpu()
            ram = probe.detect_ram_gb()
        self.assertNotEqual(cpu["model"], "unknown")
        self.assertGreater(cpu["cores_physical"], 0)
        self.assertLessEqual(cpu["cores_physical"], cpu["cores_logical"])
        self.assertGreater(ram, 0)
        self.assertLess(ram, 1024)


if __name__ == "__main__":
    unittest.main()
