"""Миграции, каталог, static и gunicorn — для Layero / Docker / Railway."""

import os
import sys
from pathlib import Path


def _project_root() -> Path:
    here = Path(__file__).resolve().parent
    if (here / "manage.py").is_file():
        return here
    if (here.parent / "manage.py").is_file():
        return here.parent
    return here


ROOT = _project_root()


def _ensure_superuser() -> None:
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "").strip()
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
    if not username or not password:
        return

    from django.contrib.auth import get_user_model

    User = get_user_model()
    user, _created = User.objects.get_or_create(
        username=username,
        defaults={"email": email, "is_staff": True, "is_superuser": True},
    )
    user.is_staff = True
    user.is_superuser = True
    if email:
        user.email = email
    user.set_password(password)
    user.save()


def main() -> None:
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

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
    _ensure_superuser()

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
