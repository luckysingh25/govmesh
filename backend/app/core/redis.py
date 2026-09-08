import redis
from app.core.config import settings

def get_redis_client():
    """Create a Redis client instance from application settings."""
    return redis.from_url(settings.redis_url, decode_responses=True)

def check_redis_connection() -> bool:
    """Return True if Redis is reachable, False otherwise."""
    try:
        r = get_redis_client()
        return bool(r.ping())
    except Exception:
        return False
