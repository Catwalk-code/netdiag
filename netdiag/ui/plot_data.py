"""Утилиты для подготовки данных графика ping."""

import re

_PING_AVG_PATTERN = re.compile(r"^ping:\s*ok,\s*avg=(\d+)\s*ms\s*$")
_TARGET_HEADER_PATTERN = re.compile(r"^\[(.+)\]$")


def parse_ping_bars(report_text):
    """Извлекает пары (имя цели, ping avg в ms) из текстового отчёта."""
    if not report_text:
        return []

    bars = []
    current_target_name = None
    for raw_line in report_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        target_match = _TARGET_HEADER_PATTERN.match(line)
        if target_match:
            current_target_name = target_match.group(1).strip()
            continue

        ping_match = _PING_AVG_PATTERN.match(line.lower())
        if ping_match and current_target_name:
            bars.append((current_target_name, int(ping_match.group(1))))
    return bars


def parse_ping_avg_ms(report_text):
    """Извлекает значения `ping avg` из текстового отчёта."""
    return [value for _, value in parse_ping_bars(report_text)]
