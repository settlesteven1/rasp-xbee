# Raspberry Pi Python Port

This directory provides a minimal Python implementation of the ESP32-XBee firmware features.
The script `rasp_xbee.py` acts as a simple NTRIP client bridge between a serial
port and an NTRIP caster. It was designed for running on a Raspberry Pi 4.

## Requirements
* Python 3.7+
* `pyserial`
* `flask`

Install the dependencies:
```bash
pip install -r requirements.txt
```

## Usage
```bash
python rasp_xbee.py --host <caster> --mountpoint <mount> \
    --username <user> --password <pass> [--device /dev/serial0]
```

The script reads NMEA sentences from the specified serial device, extracts the
latest GGA message and periodically forwards it to the NTRIP caster. Correction
messages from the caster are written back to the serial port.

## Web UI
A small Flask-based web interface is provided in `webui.py` for editing the
configuration and viewing the connection status.
Run it with:
```bash
python webui.py
```
It listens on port 5000 by default.
