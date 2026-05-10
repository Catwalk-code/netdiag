"""Проверка доступности TCP-портов."""

import socket


def run_tcp_check(host, ports, timeout_ms=800):
    """Проверяет список TCP-портов и возвращает открытые и закрытые"""
    timeout_sec = timeout_ms / 1000.0
    opened = []
    closed = []

    for port in ports:
        try:
            with socket.create_connection((host, port), timeout=timeout_sec):
                opened.append(port)
        except OSError:
            closed.append(port)

    # Считаем TCP-проверку успешной, если доступен хотя бы один из указанных портов.
    return {"ok": len(opened) > 0, "open": opened, "closed": closed}
