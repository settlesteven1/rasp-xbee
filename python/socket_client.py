import argparse
import select
import socket
import sys
import time

try:
    import serial
except ImportError:
    print("pyserial is required. Install with 'pip install pyserial'", file=sys.stderr)
    sys.exit(1)


def run_client(ser, host, port, udp=False, connect_message=None):
    while True:
        try:
            if udp:
                sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                sock.connect((host, port))
            else:
                sock = socket.create_connection((host, port))
            if connect_message:
                sock.sendall(connect_message.encode())
        except OSError as e:
            print(f"Failed to connect to {host}:{port}: {e}")
            time.sleep(5)
            continue

        while True:
            r, _, _ = select.select([ser, sock], [], [], 1.0)
            if ser in r:
                data = ser.read(ser.in_waiting or 1024)
                if data:
                    try:
                        if udp:
                            sock.send(data)
                        else:
                            sock.sendall(data)
                    except OSError:
                        break
            if sock in r:
                try:
                    data = sock.recv(1024)
                    if not data:
                        break
                    ser.write(data)
                except OSError:
                    break
        try:
            sock.close()
        except Exception:
            pass
        print(f"Disconnected from {host}:{port}, retrying...")
        time.sleep(5)


def main():
    parser = argparse.ArgumentParser(description="Serial socket client bridge")
    parser.add_argument('--device', default='/dev/serial0', help='Serial device path')
    parser.add_argument('--baudrate', type=int, default=115200, help='Serial baudrate')
    parser.add_argument('--host', required=True, help='Server hostname')
    parser.add_argument('--port', type=int, required=True, help='Server port')
    parser.add_argument('--udp', action='store_true', help='Use UDP instead of TCP')
    parser.add_argument('--connect-message', help='Message to send after connecting')
    args = parser.parse_args()

    ser = serial.Serial(args.device, args.baudrate, timeout=0)
    try:
        run_client(ser, args.host, args.port, args.udp, args.connect_message)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
