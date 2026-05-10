"""Проверка DNS-резолвинга host -> IP."""

import socket


def run_dns_check(host):
    """Пытается определить IPv4-адрес по имени хоста"""
    try:
        ip_address = socket.gethostbyname(host)
        return {"ok": True, "ip": ip_address, "error": None}
    except socket.gaierror as exc:
        return {"ok": False, "ip": None, "error": f"Ошибка DNS: {exc}"}
    except OSError as exc:
        return {"ok": False, "ip": None, "error": f"Системная ошибка DNS: {exc}"}
