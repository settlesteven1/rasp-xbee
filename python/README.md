# Raspberry Pi Python Port

This directory provides a minimal Python implementation of the ESP32-XBee firmware features.
The script `rasp_xbee.py` acts as a simple NTRIP client bridge between a serial
port and an NTRIP caster. It was designed for running on a Raspberry Pi 4.

By default the script looks for a configuration file at `/etc/rasp_xbee.conf`.
Values from this file provide defaults for command line arguments, but any
values supplied on the CLI take precedence.

## Requirements
* Python 3.7+
* `pyserial`

Install the dependency:
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

## Configuration file

`rasp_xbee.py` will attempt to read `/etc/rasp_xbee.conf` on start up. The file
uses INI syntax and values from the `DEFAULT` section are applied as argument
defaults. Command line flags override any options from the file.

Example:

```ini
[DEFAULT]
device = /dev/ttyUSB0
baudrate = 460800
host = ntrip.example.com
port = 2101
mountpoint = MY-RTCM3
username = user
password = pass
```
