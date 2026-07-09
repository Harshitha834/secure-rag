from collections import defaultdict
from datetime import datetime, timedelta


class RateLimiter:

    MAX_REQUESTS = 20
    WINDOW_SECONDS = 60
    user_requests = defaultdict(list)

    @classmethod
    def is_allowed(cls, username: str) -> bool:

        now = datetime.utcnow()

        # Remove expired timestamps
        cls.user_requests[username] = [
            ts
            for ts in cls.user_requests[username]
            if now - ts < timedelta(seconds=cls.WINDOW_SECONDS)
        ]

        if len(cls.user_requests[username]) >= cls.MAX_REQUESTS:
            return False

        cls.user_requests[username].append(now)
        return True


class UploadRateLimiter:
    MAX_REQUESTS = 5
    WINDOW_SECONDS = 3600

    user_requests = defaultdict(list)

    @classmethod
    def is_allowed(cls, username: str) -> bool:

        now = datetime.utcnow()

        # Remove expired timestamps
        cls.user_requests[username] = [
            ts
            for ts in cls.user_requests[username]
            if now - ts < timedelta(seconds=cls.WINDOW_SECONDS)
        ]

        if len(cls.user_requests[username]) >= cls.MAX_REQUESTS:
            return False

        cls.user_requests[username].append(now)
        return True