"""Сохранение отчёта диагностики в текстовый файл."""

from datetime import datetime
from pathlib import Path


def save_report(report_text, reports_dir="reports"):
    """Сохраняет отчёт в папку reports и возвращает абсолютный путь к .txt файлу."""
    target_dir = Path(reports_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = target_dir / f"netdiag_report_{timestamp}.txt"
    report_path.write_text(report_text, encoding="utf-8")
    return str(report_path.resolve())
