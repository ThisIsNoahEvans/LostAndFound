"""
Start the Flask API, then the Tkinter app. Stop the API when you close the GUI.

Usage (from project root):
    python run_dev.py

The API runs with debug=False here so only one process is spawned (Flask's
debug reloader would otherwise leave orphan servers). For debugging the API
alone, run: python backend/main.py
"""

from __future__ import annotations

import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API_URL = "http://127.0.0.1:5000/items"


def _wait_for_api(timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(API_URL, timeout=1)
            return
        except (urllib.error.URLError, OSError):
            time.sleep(0.15)
    raise RuntimeError(f"API did not respond in time: {API_URL}")


def main() -> None:
    api = subprocess.Popen(
        [
            sys.executable,
            "-c",
            (
                "from backend.main import app, init_db; "
                "init_db(); "
                "app.run(host='127.0.0.1', port=5000, debug=False, "
                "use_reloader=False)"
            ),
        ],
        cwd=str(ROOT),
    )
    try:
        _wait_for_api()
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from frontend.app import main as gui_main

        gui_main()
    finally:
        api.terminate()
        try:
            api.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api.kill()


if __name__ == "__main__":
    main()
