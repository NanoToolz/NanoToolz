import time
from collections import defaultdict, deque

REQUEST_LIMIT = 10
WARN_AT = 5
WINDOW_SECONDS = 60

_requests = defaultdict(deque)


def check_rate_limit(user_id: int, *, with_warning: bool = False):
    now = time.time()
    queue = _requests[user_id]

    while queue and now - queue[0] > WINDOW_SECONDS:
        queue.popleft()

    queue.append(now)
    count = len(queue)

    allowed = count <= REQUEST_LIMIT
    warn = count == WARN_AT

    if with_warning:
        return allowed, warn
    return allowed
