import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from app.core.config import settings

# Ensure the cache directory exists
CACHE_DIR = os.path.dirname(settings.RUC_CACHE_FILE)
if CACHE_DIR and not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def _get_cache_file_path() -> str:
    return settings.RUC_CACHE_FILE

def load_cache() -> Dict[str, Any]:
    """Loads the RUC cache from a JSON file."""
    cache_file = _get_cache_file_path()
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Cache file {cache_file} is corrupted. Starting with empty cache.")
            return {}
    return {}

def save_cache(cache_data: Dict[str, Any]):
    """Saves the RUC cache to a JSON file."""
    cache_file = _get_cache_file_path()
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving cache to {cache_file}: {e}")

def get_cached_ruc(ruc: str) -> Optional[Dict[str, Any]]:
    """Retrieves RUC data from cache if valid and not expired."""
    cache = load_cache()
    if ruc in cache:
        cached_entry = cache[ruc]
        cached_timestamp_str = cached_entry.get("timestamp")
        if cached_timestamp_str:
            cached_timestamp = datetime.fromisoformat(cached_timestamp_str)
            expiry_time = cached_timestamp + timedelta(hours=settings.RUC_CACHE_EXPIRY_HOURS)
            if datetime.now() < expiry_time:
                print(f"RUC {ruc} found in cache (valid until {expiry_time}).")
                return cached_entry.get("data")
            else:
                print(f"RUC {ruc} found in cache but expired. Expired at {expiry_time}.")
        else:
            print(f"RUC {ruc} found in cache but missing timestamp. Treating as expired.")
    return None

def set_cached_ruc(ruc: str, data: Dict[str, Any]):
    """Stores RUC data in cache with a timestamp."""
    cache = load_cache()
    cache[ruc] = {
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    save_cache(cache)
