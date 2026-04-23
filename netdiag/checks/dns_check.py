"""Проверка DNS-резолвинга host -> IP."""

import socket


def run_dns_check(host, dns_servers=None):
    """Пытается определить IPv4-адрес по имени хоста.

    Параметр dns_servers пока не используется и сохранён для совместимости
    с текущей структурой и возможным расширением в будущем.
    """
    # dns_servers оставлен в сигнатуре для совместимости с текущей структурой проекта.
    try:
        ip_address = socket.gethostbyname(host)
        return {"ok": True, "ip": ip_address, "error": None}
    except socket.gaierror as exc:
        return {"ok": False, "ip": None, "error": f"Ошибка DNS: {exc}"}
    except OSError as exc:
        return {"ok": False, "ip": None, "error": f"Системная ошибка DNS: {exc}"}
