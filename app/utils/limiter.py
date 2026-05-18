from slowapi import Limiter
from slowapi.util import get_remote_address

# Global limiter instance using client IP address for rate limiting
limiter = Limiter(key_func=get_remote_address)