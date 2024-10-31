# backend/utils/cache.py

from flask_caching import Cache
from flask import Flask

cache = Cache(config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

def init_cache(app: Flask):
    """
    Initialize caching for the Flask app.
    """
    cache.init_app(app)

class CacheResponse:
    """
    Simple cache wrapper for responses.
    """
    def __init__(self, cache_instance):
        self.cache = cache_instance

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache.set(key, value)

cache_response = CacheResponse(cache)

