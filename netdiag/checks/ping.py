import subprocess
import platform

def run_ping_check(host, count=4, timeout_ms=1000):
    system = platform.system().lower()
    cmd = ["ping", "-n", str(count), "-w", str(timeout_ms), host]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    ok = result.returncode == 0
    return "OK" if ok else "FAIL"