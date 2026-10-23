import os
from slowapi import Limiter
from slowapi.util import get_remote_address

REDIS_RATE_LIMIT_URL = os.getenv(
    "REDIS_RATE_LIMIT_URL",
    "redis://localhost:6379/2",
)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=REDIS_RATE_LIMIT_URL,
    key_prefix="shipment_tracker:",
    headers_enabled=True,
    in_memory_fallback_enabled=False,
    swallow_errors=False,
)
