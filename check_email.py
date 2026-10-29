"""Отправляет одно тестовое письмо настройками Django. Пароль в консоль не выводится."""

import os
import sys

import django
from decouple import config


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
    django.setup()

    from django.conf import settings
    from django.core.mail import send_mail

    recipient = config("EMAIL_TEST_RECIPIENT", default="")
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD or not recipient:
        print("Заполните EMAIL_HOST_USER, EMAIL_HOST_PASSWORD и EMAIL_TEST_RECIPIENT в .env")
        sys.exit(1)

    send_mail(
        "Тестовое письмо",
        "Это тестовое письмо от Django.",
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        fail_silently=False,
    )
    print(f"Письмо отправлено на {recipient}")


if __name__ == "__main__":
    main()
