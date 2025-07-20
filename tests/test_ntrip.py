import os
import socket
import sys
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

import rasp_xbee


def _make_socketpair():
    return socket.socketpair()


def test_connect_ntrip_success(monkeypatch):
    client, server = _make_socketpair()

    def fake_create_connection(addr):
        return client

    def server_thread():
        request = server.recv(1024)
        assert b"GET /MOUNT HTTP/1.1" in request
        server.sendall(b"HTTP/1.1 200 OK\r\n\r\n")

    th = threading.Thread(target=server_thread)
    th.start()

    monkeypatch.setattr(socket, 'create_connection', fake_create_connection)
    sock = rasp_xbee.connect_ntrip('localhost', 2101, 'MOUNT')
    th.join(timeout=1)
    server.close()
    sock.close()


def test_connect_ntrip_failure(monkeypatch):
    client, server = _make_socketpair()

    def fake_create_connection(addr):
        return client

    def server_thread():
        server.recv(1024)
        server.sendall(b"HTTP/1.1 401 Unauthorized\r\n\r\n")

    th = threading.Thread(target=server_thread)
    th.start()

    monkeypatch.setattr(socket, 'create_connection', fake_create_connection)
    try:
        rasp_xbee.connect_ntrip('localhost', 2101, 'MOUNT')
    except RuntimeError as e:
        assert "Bad response" in str(e)
    else:
        raise AssertionError("Expected RuntimeError")
    th.join(timeout=1)
    server.close()
    client.close()
