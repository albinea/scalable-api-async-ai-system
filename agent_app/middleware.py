import time

from django.core.cache import cache
from django.http import JsonResponse


class RateLimitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

        self.max_requests = 1000
        self.window = 60

    def __call__(self, request):

        if request.path.startswith("/api/"):

            ip = self.get_client_ip(request)

            key = f"rate_limit:{ip}"

            current = cache.get(key, 0)

            if current >= self.max_requests:

                return JsonResponse(
                    {
                        "error": "Rate limit exceeded",
                        "retry_after": self.window,
                    },
                    status=429,
                )

            if current == 0:
                cache.set(
                    key,
                    1,
                    timeout=self.window,
                )
            else:
                cache.incr(key)

        return self.get_response(request)

    def get_client_ip(self, request):

        forwarded = request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )

        if forwarded:
            return forwarded.split(",")[0].strip()

        return request.META.get(
            "REMOTE_ADDR",
            "unknown",
        )