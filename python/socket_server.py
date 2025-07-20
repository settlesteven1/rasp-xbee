import argparse
import select
import socket
import sys

try:
    import serial
except ImportError:
    print("pyserial is required. Install with 'pip install pyserial'", file=sys.stderr)
    sys.exit(1)


def run_server(ser, tcp_port, udp_port):
    server_tcp = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_tcp.bind(("", tcp_port))
    server_tcp.listen(1)

    server_udp = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    server_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_udp.bind(("", udp_port))

    tcp_clients = []
    udp_clients = set()

    while True:
        sockets = [server_tcp, server_udp] + tcp_clients + [ser]
        r, _, _ = select.select(sockets, [], [], 1.0)

        if ser in r:
            data = ser.read(ser.in_waiting or 1024)
            if data:
                for c in tcp_clients[:]:
                    try:
                        c.sendall(data)
                    except OSError:
                        tcp_clients.remove(c)
                        c.close()
                for addr in list(udp_clients):
                    try:
                        server_udp.sendto(data, addr)
                    except OSError:
                        udp_clients.discard(addr)

        if server_tcp in r:
            client, addr = server_tcp.accept()
            tcp_clients.append(client)

        if server_udp in r:
            data, addr = server_udp.recvfrom(1024)
            udp_clients.add(addr)
            if data:
                ser.write(data)

        for c in tcp_clients[:]:
            if c in r:
                data = c.recv(1024)
                if not data:
                    tcp_clients.remove(c)
                    c.close()
                else:
                    ser.write(data)


def main():
    parser = argparse.ArgumentParser(description="Serial TCP/UDP socket server bridge")
    parser.add_argument('--device', default='/dev/serial0', help='Serial device path')
    parser.add_argument('--baudrate', type=int, default=115200, help='Serial baudrate')
    parser.add_argument('--tcp-port', type=int, default=23, help='TCP listen port')
    parser.add_argument('--udp-port', type=int, default=2323, help='UDP listen port')
    args = parser.parse_args()

    ser = serial.Serial(args.device, args.baudrate, timeout=0)
    try:
        run_server(ser, args.tcp_port, args.udp_port)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
