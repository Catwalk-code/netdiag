"""Утилиты для подготовки данных графика ping."""

import re

_PING_AVG_PATTERN = re.compile(r"^ping:\s*ok,\s*avg=(\d+)\s*ms\s*$")


def parse_ping_avg_ms(report_text):
    """Извлекает значения `ping avg` из текстового отчёта."""
    if not report_text:
        return []

    values = []
    for line in report_text.splitlines():
        match = _PING_AVG_PATTERN.match(line.strip().lower())
        if match:
            values.append(int(match.group(1)))
    return values
