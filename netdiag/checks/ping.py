"""Проверка доступности узла через ping (Windows)."""

import platform
import re
import subprocess


def _parse_avg_ms(output: str) -> int | None:
    """Извлекает среднее время из вывода ping в RU/EN локали."""
    patterns = (
        r"Average\s*=\s*(\d+)\s*ms",  # EN
        r"Среднее\s*=\s*(\d+)\s*(?:мс|ms)?",  # RU
    )
    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def run_ping_check(host: str, count: int = 4, timeout_ms: int = 1000) -> dict:
    """Запускает Windows ping и возвращает результат в структурированном виде."""
    if platform.system() != "Windows":
        return {"ok": False, "avg_ms": None, "raw": "Диагностика ping поддерживается только в Windows."}

    cmd = ["ping", "-n", str(count), "-w", str(timeout_ms), host]
    command_timeout_sec = max(5, count * max(timeout_ms, 1) / 1000 + 5)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="cp866",
            errors="ignore",
            timeout=command_timeout_sec,
            check=False,
        )
    except FileNotFoundError:
        return {"ok": False, "avg_ms": None, "raw": "Команда ping не найдена в системе."}
    except subprocess.TimeoutExpired:
        return {"ok": False, "avg_ms": None, "raw": "Команда ping завершилась по таймауту."}
    except OSError as exc:
        return {"ok": False, "avg_ms": None, "raw": f"Ошибка запуска ping: {exc}"}

    output = ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
    avg_ms = _parse_avg_ms(output)
    return {"ok": result.returncode == 0, "avg_ms": avg_ms, "raw": output}
