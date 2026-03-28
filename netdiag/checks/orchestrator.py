from netdiag.config import load_config


def run_all_checks(config_path: str = "targets.json") -> str:
    config = load_config(config_path)
    lines = []

    for target in config.targets:
        ports = target.ports if target.ports is not None else config.defaults.ports
        lines.append(f"[{target.name}] host={target.host}, ports={ports}")
        lines.append("  ping: TODO")
        lines.append("  dns:  TODO")
        lines.append("  tcp:  TODO")
        lines.append("")

    return "\n".join(lines)