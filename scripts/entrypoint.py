"""Миграции, каталог, static и gunicorn — для Layero / Docker / Railway."""

import os
import sys
from pathlib import Path


def _project_root() -> Path:
    here = Path(__file__).resolve().parent
    # root entrypoint.py -> here; scripts/entrypoint.py -> here.parent
    if (here / "manage.py").is_file():
        return here
    if (here.parent / "manage.py").is_file():
        return here.parent
    return here


ROOT = _project_root()


def main() -> None:
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    sqlite_path = os.environ.get("SQLITE_PATH")
    if sqlite_path:
        Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

    import django
    from django.contrib.auth import get_user_model
    from django.core.management import call_command

    django.setup()

    from app.models import Category

    call_command("migrate", interactive=False)
    if not Category.objects.exists():
        call_command("loaddata", "catalog")
    call_command("collectstatic", interactive=False, verbosity=0)

    # Опционально: админ из env (для просмотра заявок на Layero).
    if os.environ.get("DJANGO_SUPERUSER_USERNAME") and os.environ.get(
        "DJANGO_SUPERUSER_PASSWORD"
    ):
        User = get_user_model()
        username = os.environ["DJANGO_SUPERUSER_USERNAME"]
        if not User.objects.filter(username=username).exists():
            call_command("createsuperuser", interactive=False)

    port = os.environ.get("PORT", "8000")
    os.execvp(
        "gunicorn",
        [
            "gunicorn",
            "website.wsgi:application",
            "--bind",
            f"0.0.0.0:{port}",
            "--chdir",
            str(ROOT),
            "--pythonpath",
            str(ROOT),
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
