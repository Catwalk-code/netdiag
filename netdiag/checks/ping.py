import subprocess
import platform
import re

def _parse_avg_ms(output: str):
    
    m_en = re.search(r"Average\s*=\s*(\d+)\s*ms", output, re.IGNORECASE)
    if m_en:
        return int(m_en.group(1))

    m_ru = re.search(r"Среднее\s*=\s*(\d+)", output, re.IGNORECASE)
    if m_ru:
        return int(m_ru.group(1))

    return None

def run_ping_check(host, count=4, timeout_ms=1000):
    system = platform.system().lower()
    cmd = ["ping", "-n", str(count), "-w", str(timeout_ms), host]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="cp866", errors="ignore")
    output = (result.stdout or "") + "\n" + (result.stderr or "")
    avg_ms = _parse_avg_ms(output)

    return {
        "ok": result.returncode == 0,
        "avg_ms": avg_ms,
        "raw": output,
    }