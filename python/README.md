# Raspberry Pi Python Port

This directory provides a minimal Python implementation of the ESP32-XBee firmware features.
The script `rasp_xbee.py` can operate as an NTRIP client, server or caster and was designed for running on a Raspberry Pi 4.

## Requirements
* Python 3.7+
* `pyserial`

Install the dependency:
```bash
pip install -r requirements.txt
```

## Usage

### Client
```bash
python rasp_xbee.py --mode client --host <caster> --mountpoint <mount> \
    --username <user> --password <pass>
```
Connects to an external caster and forwards corrections to the serial port.

### Server
```bash
python rasp_xbee.py --mode server --port 2101
```
Waits for a base station connection and writes received data to the serial device.

### Caster
```bash
python rasp_xbee.py --mode caster --port 2101 --mountpoint MOUNT \
    [--username user --password pass]
```
Allows multiple NTRIP clients to connect to the caster. Corrections from the serial device are forwarded to all clients.
