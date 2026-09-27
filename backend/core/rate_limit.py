from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared limiter instance used by the app and routers.
# Keeping it outside backend.main avoids circular imports.
limiter = Limiter(key_func=get_remote_address)
