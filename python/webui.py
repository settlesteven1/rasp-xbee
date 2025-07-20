import json
import os
import socket
from flask import Flask, request, redirect, url_for, render_template_string

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

DEFAULT_CONFIG = {
    "device": "/dev/serial0",
    "baudrate": 115200,
    "host": "",
    "port": 2101,
    "mountpoint": "",
    "username": "",
    "password": ""
}


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            cfg = json.load(f)
    else:
        cfg = {}
    result = DEFAULT_CONFIG.copy()
    result.update(cfg)
    return result


def save_config(cfg):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f, indent=2)


app = Flask(__name__)

CONFIG_TEMPLATE = """
<!doctype html>
<title>Config</title>
<h1>Configuration</h1>
<form method=post>
  <label>Device:<input name=device value="{{cfg['device']}}"></label><br>
  <label>Baudrate:<input name=baudrate value="{{cfg['baudrate']}}"></label><br>
  <label>Host:<input name=host value="{{cfg['host']}}"></label><br>
  <label>Port:<input name=port value="{{cfg['port']}}"></label><br>
  <label>Mountpoint:<input name=mountpoint value="{{cfg['mountpoint']}}"></label><br>
  <label>Username:<input name=username value="{{cfg['username']}}"></label><br>
  <label>Password:<input name=password type=password value="{{cfg['password']}}"></label><br>
  <input type=submit value=Save>
</form>
<a href="{{ url_for('status') }}">Status</a>
"""

STATUS_TEMPLATE = """
<!doctype html>
<title>Status</title>
<h1>Status</h1>
<p>NTRIP connection: {{ status }}</p>
<a href="{{ url_for('config') }}">Back to config</a>
"""


@app.route('/', methods=['GET', 'POST'])
def config():
    cfg = load_config()
    if request.method == 'POST':
        for key in DEFAULT_CONFIG:
            val = request.form.get(key)
            if val is not None:
                if key in ('baudrate', 'port'):
                    try:
                        cfg[key] = int(val)
                    except ValueError:
                        pass
                else:
                    cfg[key] = val
        save_config(cfg)
        return redirect(url_for('config'))
    return render_template_string(CONFIG_TEMPLATE, cfg=cfg)


@app.route('/status')
def status():
    cfg = load_config()
    status = 'disconnected'
    if cfg.get('host'):
        try:
            with socket.create_connection((cfg['host'], cfg['port']), timeout=2):
                status = 'connected'
        except OSError:
            status = 'disconnected'
    return render_template_string(STATUS_TEMPLATE, status=status)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
