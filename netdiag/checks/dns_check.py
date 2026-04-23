import socket
def run_dns_check(host, dns_servers):
    try:
        ip=socket.gethostbyname(host)
        return f"OK (IP: {ip})"
    except Exception as e:
        return f"FAIL ({e})"