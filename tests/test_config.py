import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

import rasp_xbee


def test_load_config_defaults():
    parser = rasp_xbee.create_parser()
    args = parser.parse_args(['--host', 'example.com', '--mountpoint', 'MOUNT'])
    assert args.device == '/dev/serial0'
    assert args.baudrate == 115200
    assert args.port == 2101
    assert args.host == 'example.com'
    assert args.mountpoint == 'MOUNT'
    assert args.username is None
    assert args.password is None


def test_load_config_custom():
    parser = rasp_xbee.create_parser()
    args = parser.parse_args([
        '--device', '/dev/ttyUSB0',
        '--baudrate', '9600',
        '--host', 'host',
        '--port', '1234',
        '--mountpoint', 'POINT',
        '--username', 'u',
        '--password', 'p'
    ])
    assert args.device == '/dev/ttyUSB0'
    assert args.baudrate == 9600
    assert args.port == 1234
    assert args.username == 'u'
    assert args.password == 'p'
