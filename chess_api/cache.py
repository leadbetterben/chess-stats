import json
from pathlib import Path

DATA_DIR = Path("data")

def load_json(filename, default=None):
    path = DATA_DIR / filename
    if path.exists():
        return json.loads(path.read_text())
    return default


def save_json(filename, data):
    path = DATA_DIR / filename
    path.write_text(json.dumps(data, indent=2))
