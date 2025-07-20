import configparser
from pathlib import Path

CONFIG_PATH = '/etc/rasp_xbee.conf'


def load_config(path: str = CONFIG_PATH) -> dict:
    """Load configuration from *path* if it exists.

    Returns a dictionary of options. Unknown files result in an
    empty dictionary.
    """
    parser = configparser.ConfigParser()
    file = Path(path)
    if file.is_file():
        parser.read(path)
        # Use DEFAULT section for simplicity
        return dict(parser.defaults())
    return {}
