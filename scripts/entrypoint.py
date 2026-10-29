"""Миграции, каталог, static и gunicorn — для Layero / Docker / Railway."""

import os
from pathlib import Path


def main() -> None:
    sqlite_path = os.environ.get("SQLITE_PATH")
    if sqlite_path:
        Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

    import django
    from django.core.management import call_command

    django.setup()

    from app.models import Category

    call_command("migrate", interactive=False)
    if not Category.objects.exists():
        call_command("loaddata", "catalog")
    call_command("collectstatic", interactive=False, verbosity=0)

    port = os.environ.get("PORT", "8000")
    os.execvp(
        "gunicorn",
        [
            "gunicorn",
            "website.wsgi:application",
            "--bind",
            f"0.0.0.0:{port}",
            "--workers",
            "1",
            "--threads",
            "4",
            "--timeout",
            "60",
        ],
    )


if __name__ == "__main__":
    main()
