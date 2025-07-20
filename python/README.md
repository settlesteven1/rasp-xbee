# Raspberry Pi Python Port

This directory provides a minimal Python implementation of the ESP32-XBee firmware features.
The script `rasp_xbee.py` acts as a simple NTRIP client bridge between a serial
port and an NTRIP caster. It was designed for running on a Raspberry Pi 4.

## Requirements
* Python 3.7+
* `pyserial`

Install the dependency:
```bash
pip install -r requirements.txt
```

## Usage
`rasp_xbee.py` now provides several sub-commands. Common serial options are
`--device` and `--baudrate`.

### NTRIP client
```bash
python rasp_xbee.py ntrip --host <caster> --mountpoint <mount> \
    --username <user> --password <pass>
```

The script reads NMEA sentences from the serial device, extracts the latest GGA
message and periodically forwards it to the NTRIP caster. Corrections from the
caster are written back to the serial port.

## Socket Server
`socket_server.py` (or `rasp_xbee.py server`) exposes the serial port over TCP
and UDP similarly to the firmware's socket server.

```bash
python socket_server.py [--tcp-port 23] [--udp-port 2323] [--device /dev/serial0]
```

## Socket Client
`socket_client.py` (or `rasp_xbee.py client`) connects the serial port to a
remote TCP or UDP host.

```bash
python socket_client.py --host <host> --port <port> [--udp] \
    [--connect-message "hello"] [--device /dev/serial0]
```
