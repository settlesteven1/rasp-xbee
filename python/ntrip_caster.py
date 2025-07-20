import argparse
import base64
import select
import socket
import sys

try:
    import serial
except ImportError:  # pragma: no cover - environment check only
    print("pyserial is required. Install with 'pip install pyserial'", file=sys.stderr)
    sys.exit(1)


class Client:
    def __init__(self, conn):
        self.conn = conn
        self.conn.setblocking(False)


def _parse_headers(data):
    lines = data.split('\r\n')
    headers = {}
    for line in lines[1:]:
        if ':' in line:
            k, v = line.split(':', 1)
            headers[k.strip().lower()] = v.strip()
    return lines[0], headers


def _send_sourcetable(conn, mountpoint, username, user_agent):
    stream = f"STR;{mountpoint};;;;;;;;0.00;0.00;0;0;;none;{'N' if not username else 'B'};N;0;\r\nENDSOURCETABLE"
    body = stream.encode()
    header = (
        f"SOURCETABLE 200 OK\r\n"
        f"Server: NTRIP Caster/1.0\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n\r\n"
    )
    if 'ntrip' not in user_agent.lower():
        header = header.replace('SOURCETABLE 200 OK', 'HTTP/1.0 200 OK')
    conn.sendall(header.encode() + body)


def _send_unauthorized(conn, mountpoint):
    message = b"Authorization Required"
    header = (
        f"HTTP/1.0 401 Unauthorized\r\n"
        f"Server: NTRIP Caster/1.0\r\n"
        f"WWW-Authenticate: Basic realm=\"/{mountpoint}\"\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(message)}\r\n"
        f"Connection: close\r\n\r\n"
    )
    conn.sendall(header.encode() + message)


def _handle_handshake(conn, mountpoint, username, password):
    data = conn.recv(1024).decode(errors='ignore')
    if not data:
        conn.close()
        return None
    first, headers = _parse_headers(data)
    if not first.startswith('GET'):
        conn.sendall(b"HTTP/1.1 405 Method Not Allowed\r\nAllow: GET\r\n\r\n")
        conn.close()
        return None
    path = first.split()[1]
    if path.startswith('/'):
        path = path[1:]
    user_agent = headers.get('user-agent', '')
    if path != mountpoint:
        _send_sourcetable(conn, mountpoint, username, user_agent)
        conn.close()
        return None
    if username:
        auth = headers.get('authorization', '')
        token = base64.b64encode(f"{username}:{password}".encode()).decode()
        if auth != f"Basic {token}":
            _send_unauthorized(conn, mountpoint)
            conn.close()
            return None
    conn.sendall(b"ICY 200 OK\r\n\r\n")
    return Client(conn)


def run_caster(args):
    """Run a very small NTRIP caster."""
    ser = serial.Serial(args.device, args.baudrate, timeout=0)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.bind, args.port))
    sock.listen(5)

    clients = []
    try:
        while True:
            rlist = [sock, ser] + [c.conn for c in clients]
            r, _, _ = select.select(rlist, [], [], 1.0)
            if sock in r:
                conn, _ = sock.accept()
                c = _handle_handshake(conn, args.mountpoint, args.username, args.password)
                if c:
                    clients.append(c)
            if ser in r:
                data = ser.read(1024)
                if data:
                    dead = []
                    for c in clients:
                        try:
                            c.conn.sendall(data)
                        except OSError:
                            dead.append(c)
                    for d in dead:
                        d.conn.close()
                        clients.remove(d)
            for c in clients:
                if c.conn in r:
                    if not c.conn.recv(1024):
                        c.conn.close()
                        clients.remove(c)
    finally:
        for c in clients:
            c.conn.close()
        sock.close()
        ser.close()


def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument('--bind', default='0.0.0.0', help='Address to bind')
    parser.add_argument('--port', type=int, default=2101, help='TCP listen port')
    parser.add_argument('--mountpoint', default='MOUNT', help='Caster mountpoint')
    parser.add_argument('--username', default='', help='Require username')
    parser.add_argument('--password', default='', help='Require password')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Simple NTRIP caster')
    ap.add_argument('--device', default='/dev/serial0', help='Serial device path')
    ap.add_argument('--baudrate', type=int, default=115200, help='Serial baudrate')
    add_arguments(ap)
    args = ap.parse_args()
    try:
        run_caster(args)
    except KeyboardInterrupt:
        pass
