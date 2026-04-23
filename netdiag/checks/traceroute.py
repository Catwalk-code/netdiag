"""Проверка маршрута до узла через tracert (Windows)."""

import platform
import subprocess


def _is_hop_line(line: str) -> bool:
    """Проверяет, содержит ли строка информацию о переходе маршрута."""
    normalized = f" {line} "
    return " ms " in normalized or " <1 ms" in line or "Request timed out." in line


def _compact_tracert_output(raw_output: str, max_lines: int = 8) -> str:
    """Формирует компактный текст по ключевым строкам tracert."""
    lines = [line.strip() for line in raw_output.splitlines() if line.strip()]
    hop_lines = [line for line in lines if _is_hop_line(line)]
    if not hop_lines:
        return "Нет данных по переходам маршрута."
    return "\n".join(hop_lines[:max_lines])


def run_traceroute(host: str, max_hops: int = 15, timeout_ms: int = 1000) -> dict:
    """Запускает tracert и возвращает краткий и полный вывод."""
    if platform.system() != "Windows":
        return {"ok": False, "summary": "Traceroute поддерживается только в Windows.", "raw": ""}

    cmd = ["tracert", "-d", "-h", str(max_hops), "-w", str(timeout_ms), host]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="cp866",
            errors="ignore",
            timeout=max(10, max_hops * max(timeout_ms, 1) / 1000 + 10),
            check=False,
        )
    except FileNotFoundError:
        return {"ok": False, "summary": "Команда tracert не найдена в системе.", "raw": ""}
    except subprocess.TimeoutExpired:
        return {"ok": False, "summary": "Команда tracert завершилась по таймауту.", "raw": ""}
    except OSError as exc:
        return {"ok": False, "summary": f"Ошибка запуска tracert: {exc}", "raw": ""}

    raw_output = ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
    summary = _compact_tracert_output(raw_output)
    return {"ok": result.returncode == 0, "summary": summary, "raw": raw_output}
