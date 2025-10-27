import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SERVICE_CACHE_PATH = BASE_DIR / "service_catalog_cache.json"


def _load_json(path):
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def _save_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def load_service_cache():
    return _load_json(SERVICE_CACHE_PATH)


def save_service_cache(cache):
    _save_json(SERVICE_CACHE_PATH, cache)

