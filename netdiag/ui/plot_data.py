"""Утилиты для подготовки данных графиков диагностик."""

from dataclasses import dataclass
import re

_PING_AVG_PATTERN = re.compile(r"^ping:\s*ok,\s*avg=(\d+)\s*ms\s*$")
_DNS_OK_PATTERN = re.compile(r"^dns:\s*ok\b")
_DNS_FAIL_PATTERN = re.compile(r"^dns:\s*(fail|error)\b")
_TCP_OK_PATTERN = re.compile(r"^tcp:\s*ok\b")
_TCP_FAIL_PATTERN = re.compile(r"^tcp:\s*(fail|error)\b")
_TARGET_HEADER_PATTERN = re.compile(r"^\[(.+)\]$")


@dataclass
class TargetChecks:
    """Сводные результаты проверок по цели."""

    name: str
    ping_avg_ms: int | None = None
    dns_ok: bool | None = None
    tcp_ok: bool | None = None


def parse_target_checks(report_text):
    """Извлекает результаты ping/DNS/TCP по целям из текстового отчёта."""
    if not report_text:
        return []

    targets: list[TargetChecks] = []
    current_target: TargetChecks | None = None
    for raw_line in report_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        target_match = _TARGET_HEADER_PATTERN.match(line)
        if target_match:
            if current_target is not None:
                targets.append(current_target)
            current_target = TargetChecks(name=target_match.group(1).strip())
            continue

        if current_target is None:
            continue

        line_lower = line.lower()
        ping_match = _PING_AVG_PATTERN.match(line_lower)
        if ping_match:
            current_target.ping_avg_ms = int(ping_match.group(1))
            continue

        if _DNS_OK_PATTERN.match(line_lower):
            current_target.dns_ok = True
            continue
        if _DNS_FAIL_PATTERN.match(line_lower):
            current_target.dns_ok = False
            continue

        if _TCP_OK_PATTERN.match(line_lower):
            current_target.tcp_ok = True
            continue
        if _TCP_FAIL_PATTERN.match(line_lower):
            current_target.tcp_ok = False
            continue

    if current_target is not None:
        targets.append(current_target)

    return targets


def parse_ping_bars(report_text):
    """Извлекает пары (имя цели, ping avg в ms) из текстового отчёта."""
    return [
        (target.name, target.ping_avg_ms)
        for target in parse_target_checks(report_text)
        if target.ping_avg_ms is not None
    ]


def parse_ping_avg_ms(report_text):
    """Извлекает значения `ping avg` из текстового отчёта."""
    return [value for _, value in parse_ping_bars(report_text)]
