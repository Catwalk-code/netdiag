"""Утилиты для подготовки данных графика ping."""

import re


def parse_ping_avg_ms(report_text):
    """Извлекает значения `ping avg` из текстового отчёта."""
    if not report_text:
        return []

    values = []
    pattern = re.compile(r"^ping:\s*OK,\s*avg=(\d+)\s*ms\s*$", re.IGNORECASE)
    for line in report_text.splitlines():
        match = pattern.match(line.strip())
        if match:
            values.append(int(match.group(1)))
    return values
