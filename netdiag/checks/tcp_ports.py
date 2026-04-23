import socket

def run_tcp_check(host, ports, timeout_ms=800):
    timeout_sec = timeout_ms / 1000
    opened = []
    closed = []

    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout_sec)
        try:
            s.connect((host, port))
            opened.append(port)
        except Exception:
            closed.append(port)
        finally:
            s.close()
        
        return f"OK (open: {opened}, closed: {closed})"