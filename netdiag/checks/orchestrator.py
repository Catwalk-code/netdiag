from netdiag.config import load_config
from netdiag.checks.ping import run_ping_check
from netdiag.checks.dns_check import run_dns_check
from netdiag.checks.tcp_ports import run_tcp_check

def run_all_checks(config_path: str = "targets.json"):
    config = load_config(config_path)
    lines = []

    for target in config.targets:
        ports = target.ports if target.ports is not None else config.defaults.ports
        lines.append(f"[{target.name}]")
        lines.append(f"host: {target.host}")
        lines.append(f"ports: {ports}")

        try:
            ping_result = run_ping_check(
                host=target.host,
                count=config.defaults.ping_count,
                timeout_ms=config.defaults.ping_timeout_ms,
            )
            lines.append(f"ping: {ping_result}")
        except Exception as e:
            lines.append(f"ping: ERROR ({e})")

        try:
            dns_result = run_dns_check(
                host=target.host,
                dns_servers=config.defaults.dns_servers,
            )
            lines.append(f"dns: {dns_result}")
        except Exception as e:
            lines.append(f"dns: ERROR ({e})")

        try:
            tcp_result = run_tcp_check(
                host=target.host,
                ports=ports,
                timeout_ms=config.defaults.tcp_timeout_ms,
            )
            lines.append(f"tcp: {tcp_result}")
        except Exception as e:
            lines.append(f"tcp: ERROR ({e})")

        lines.append("-"*40)  
    return "\n".join(lines)