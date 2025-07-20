import argparse
import base64
import select
import socket
import sys
import time

try:
    import serial
except ImportError:
    print("pyserial is required. Install with 'pip install pyserial'", file=sys.stderr)
    sys.exit(1)


def connect_ntrip(host, port, mountpoint, user=None, password=None):
    sock = socket.create_connection((host, port))
    headers = [f"GET /{mountpoint} HTTP/1.1",
               "User-Agent: rasp-xbee-py",]
    if user and password:
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        headers.append(f"Authorization: Basic {token}")
    headers.append("\r\n")
    request = "\r\n".join(headers)
    sock.sendall(request.encode())
    resp = sock.recv(1024)
    if b"200" not in resp:
        raise RuntimeError(f"Bad response from caster: {resp.splitlines()[0].decode(errors='ignore')}")
    return sock


def bridge(args):
    ser = serial.Serial(args.device, args.baudrate, timeout=0)
    sock = connect_ntrip(args.host, args.port, args.mountpoint, args.username, args.password)
    latest_gga = b""
    last_gga_sent = 0.0
    while True:
        r, _, _ = select.select([ser, sock], [], [], 1.0)
        if ser in r:
            data = ser.read(1024)
            if data:
                if data.startswith(b"$GPGGA") or data.startswith(b"$GNGGA"):
                    latest_gga = data.strip() + b"\r\n"
                # forward all serial data to socket? Not required except GGA
        if sock in r:
            data = sock.recv(1024)
            if not data:
                raise RuntimeError("Caster disconnected")
            ser.write(data)
        if latest_gga and time.time() - last_gga_sent > 15:
            sock.sendall(latest_gga)
            last_gga_sent = time.time()


def main():
    parser = argparse.ArgumentParser(description="Simple NTRIP client bridge for Raspberry Pi")
    parser.add_argument('--device', default='/dev/serial0', help='Serial device path')
    parser.add_argument('--baudrate', type=int, default=115200, help='Serial baudrate')
    parser.add_argument('--host', required=True, help='NTRIP caster hostname')
    parser.add_argument('--port', type=int, default=2101, help='NTRIP caster port')
    parser.add_argument('--mountpoint', required=True, help='Mountpoint to connect to')
    parser.add_argument('--username', help='NTRIP username')
    parser.add_argument('--password', help='NTRIP password')
    args = parser.parse_args()

    try:
        bridge(args)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
