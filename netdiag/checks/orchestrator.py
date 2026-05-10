from netdiag.config import load_config
from netdiag.checks.ping import run_ping_check
from netdiag.checks.dns_check import run_dns_check
from netdiag.checks.tcp_ports import run_tcp_check


def _format_ping_line(result):
    """Формирует строку результата ping."""
    if result.get("ok"):
        avg_ms = result.get("avg_ms")
        avg_value = f"{avg_ms} ms" if avg_ms is not None else "н/д"
        return f"ping: OK, avg={avg_value}"
    return "ping: FAIL"


def _format_dns_line(result):
    """Формирует строку результата DNS-проверки."""
    if result.get("ok"):
        return f"dns: OK (IP: {result.get('ip')})"
    return f"dns: FAIL ({result.get('error', 'неизвестная ошибка')})"


def _format_tcp_line(result):
    """Формирует строку результата TCP-проверки."""
    open_ports = result.get("open", [])
    closed_ports = result.get("closed", [])
    status = "OK" if result.get("ok") else "FAIL"
    return f"tcp: {status} (open: {open_ports}, closed: {closed_ports})"


def run_all_checks(config_path="targets.json"):
    """Запускает все проверки и возвращает человекочитаемый итоговый отчёт."""
    config = load_config(config_path)
    lines = []

    for target in config.targets:
        ports = target.ports if target.ports is not None else config.defaults.ports
        lines.append(f"[{target.name}]")
        lines.append(f"host: {target.host}")
        lines.append(f"ports: {ports}")  # Список тестируемых портов для наглядности.

        try:
            ping_result = run_ping_check(
                host=target.host,
                count=config.defaults.ping_count,
                timeout_ms=config.defaults.ping_timeout_ms,
            )
            lines.append(_format_ping_line(ping_result))
        except Exception as e:
            lines.append(f"ping: ERROR ({e})")

        try:
            dns_result = run_dns_check(
                host=target.host,
            )
            lines.append(_format_dns_line(dns_result))
        except Exception as e:
            lines.append(f"dns: ERROR ({e})")

        try:
            tcp_result = run_tcp_check(
                host=target.host,
                ports=ports,
                timeout_ms=config.defaults.tcp_timeout_ms,
            )
            lines.append(_format_tcp_line(tcp_result))
        except Exception as e:
            lines.append(f"tcp: ERROR ({e})")

        lines.append("-" * 40)
    return "\n".join(lines)
