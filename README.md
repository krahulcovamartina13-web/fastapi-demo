# FastAPI demo – API testy

Jednoduché REST API pro úkoly (`/health`, `/tasks` CRUD) postavené na FastAPI a k němu automatizované API testy v pytestu.

## Spuštění

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# testy
pytest -v

# volitelně spuštění API (dokumentace na http://127.0.0.1:8000/docs)
uvicorn app.main:app --reload
```

## Struktura

- `app/main.py` – aplikace (endpointy `/health`, `/tasks`)
- `tests/test_api.py` – integrační testy přes FastAPI TestClient
- `tests/test_live_server.py` – testy proti běžícímu serveru přes httpx
- `tests/conftest.py` – sdílené fixtures
