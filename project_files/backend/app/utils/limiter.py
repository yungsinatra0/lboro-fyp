from slowapi.util import get_remote_address
from slowapi import Limiter

# Initialising rate limiting middleware that will be used to limit the number of requests from a single IP address for each endpoint
limiter = Limiter(key_func=get_remote_address)