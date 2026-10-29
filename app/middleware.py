"""Простые защитные заголовки и ограничение частоты POST-запросов."""

from __future__ import annotations

import time
from collections import defaultdict, deque

from django.http import HttpRequest, HttpResponse, JsonResponse


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("X-Frame-Options", "DENY")
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        return response


class RateLimitMiddleware:
    """Ограничение частоты POST к корзине и заявкам без внешних зависимостей."""

    LIMITS = {
        "/place-order/": (5, 60),
        "/add-to-cart": (40, 60),
        "/update-cart/": (60, 60),
    }

    def __init__(self, get_response):
        self.get_response = get_response
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.method == "POST":
            for path, (limit, window) in self.LIMITS.items():
                if request.path.startswith(path.rstrip("/")) or request.path == path:
                    blocked = self._is_limited(request, path, limit, window)
                    if blocked:
                        if request.headers.get("x-requested-with") == "XMLHttpRequest" or (
                            "application/json" in request.headers.get("Accept", "")
                        ):
                            return JsonResponse(
                                {"error": "Слишком много запросов. Подождите минуту."},
                                status=429,
                            )
                        return HttpResponse(
                            "Слишком много запросов. Подождите минуту и попробуйте снова.",
                            status=429,
                            content_type="text/plain; charset=utf-8",
                        )
        return self.get_response(request)

    def _is_limited(self, request: HttpRequest, path: str, limit: int, window: int) -> bool:
        key = f"{self._client_ip(request)}:{path}"
        now = time.monotonic()
        bucket = self._hits[key]
        while bucket and now - bucket[0] > window:
            bucket.popleft()
        if len(bucket) >= limit:
            return True
        bucket.append(now)
        return False

    @staticmethod
    def _client_ip(request: HttpRequest) -> str:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
