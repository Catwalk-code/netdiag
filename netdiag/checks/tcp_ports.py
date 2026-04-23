"""Проверка доступности TCP-портов."""

import socket


def run_tcp_check(host: str, ports: list[int], timeout_ms: int = 800) -> dict:
    """Проверяет список TCP-портов и возвращает открытые и закрытые."""
    timeout_sec = timeout_ms / 1000.0
    opened: list[int] = []
    closed: list[int] = []

    for port in ports:
        try:
            with socket.create_connection((host, port), timeout=timeout_sec):
                opened.append(port)
        except OSError:
            closed.append(port)

    return {"ok": len(closed) == 0, "open": opened, "closed": closed}
