import argparse
import select
import socket
import sys

try:
    import serial
except ImportError:  # pragma: no cover - environment check only
    print("pyserial is required. Install with 'pip install pyserial'", file=sys.stderr)
    sys.exit(1)


def run_server(args):
    """Accept RTCM from a base station and forward to a serial port."""
    ser = serial.Serial(args.device, args.baudrate, timeout=0)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.bind, args.port))
    sock.listen(1)

    conn = None
    try:
        while True:
            rlist = [sock, ser]
            if conn:
                rlist.append(conn)
            r, _, _ = select.select(rlist, [], [], 1.0)
            if sock in r:
                if conn:
                    conn.close()
                conn, addr = sock.accept()
                conn.setblocking(False)
                print(f"Base connected from {addr}")
            if conn and conn in r:
                data = conn.recv(1024)
                if not data:
                    conn.close()
                    conn = None
                else:
                    ser.write(data)
            if ser in r:
                # Discard any data coming from serial
                ser.read(1024)
    finally:
        if conn:
            conn.close()
        sock.close()
        ser.close()


def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument('--bind', default='0.0.0.0', help='Address to bind')
    parser.add_argument('--port', type=int, default=2101, help='TCP listen port')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Simple NTRIP server')
    ap.add_argument('--device', default='/dev/serial0', help='Serial device path')
    ap.add_argument('--baudrate', type=int, default=115200, help='Serial baudrate')
    add_arguments(ap)
    args = ap.parse_args()
    try:
        run_server(args)
    except KeyboardInterrupt:
        pass
