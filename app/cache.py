"""Redis-backed response cache for a handful of hot listing endpoints.

Cache key is `cache:<namespace>:<raw query string>`. Every Redis call is
wrapped so a cache failure just falls back to the uncached path silently.
"""

from functools import wraps

import redis
from flask import current_app, request

from app.utils import get_logger

logger = get_logger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = redis.Redis.from_url(
            current_app.config["CACHE_REDIS_URL"],
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    return _client


def _key(namespace):
    return f"cache:{namespace}:{request.query_string.decode()}"


def cached_response(namespace, ttl=None):
    """Caches a view's JSON response, keyed by namespace + exact query string."""

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            key = _key(namespace)

            try:
                cached = _get_client().get(key)
            except redis.exceptions.RedisError:
                logger.warning(
                    "Cache read failed for %s - falling back to live query", key
                )
                return view(*args, **kwargs)

            if cached is not None:
                return current_app.response_class(cached, mimetype="application/json")

            response = current_app.make_response(view(*args, **kwargs))
            if response.status_code == 200:
                try:
                    _get_client().set(
                        key,
                        response.get_data(),
                        ex=ttl or current_app.config["CACHE_DEFAULT_TTL"],
                    )
                except redis.exceptions.RedisError:
                    logger.warning("Cache write failed for %s", key)
            return response

        return wrapped

    return decorator


def invalidate(namespace):
    """Clears every cached variant of a listing (see contracts/invalidation-map.md)."""
    try:
        client = _get_client()
        keys = list(client.scan_iter(match=f"cache:{namespace}:*"))
        if keys:
            client.delete(*keys)
    except redis.exceptions.RedisError:
        logger.warning("Cache invalidation failed for namespace=%s", namespace)
