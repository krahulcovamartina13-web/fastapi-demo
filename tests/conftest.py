import os
import socket
import subprocess
import sys
import time

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app, reset_db

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def client():
    """In-process klient – volá API přes celý ASGI stack (routing, validace, serializace)."""
    reset_db()
    with TestClient(app) as c:
        yield c


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def live_server():
    """Spustí skutečný uvicorn server v samostatném procesu a vrátí jeho base URL."""
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base_url = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            if httpx.get(f"{base_url}/health").status_code == 200:
                break
        except httpx.ConnectError:
            time.sleep(0.1)
    else:
        proc.terminate()
        pytest.fail("Server se nepodařilo spustit")
    yield base_url
    proc.terminate()
    proc.wait(timeout=5)
