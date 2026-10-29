# Деплой

Секреты (`SECRET_KEY`, почта, ключ Яндекс.Карт) задаются в панели хостинга, не в git.

## Layero (рекомендуется для РФ, Free без карты)

В репозитории есть `layero.json`: runtime `python_web`, старт `python scripts/entrypoint.py` (migrate + каталог из fixture + collectstatic + gunicorn).

1. Запушьте папку `website` на GitHub (`media/` и `app/fixtures/` должны быть в репозитории).
2. [app.layero.ru](https://app.layero.ru/) → новый проект из GitHub **или** в корне проекта:
   `npx layero@latest deploy -t python_web -y`
3. Variables:

   | Имя | Значение |
   | --- | --- |
   | `SECRET_KEY` | длинная случайная строка |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `*` или `*.layero.app` / точный хост |
   | `CSRF_TRUSTED_ORIGINS` | `https://<проект>.layero.app` |
   | `DB_ENGINE` | `sqlite` |
   | `YANDEX_MAPS_API_KEY` | по желанию |

4. Диск контейнера эфемерный: каталог при старте снова грузится из fixture; заявки после cold start не сохраняются. Постоянные данные — только с внешним/Layero Postgres (обычно Pro).

## Railway

Подходит, если вы готовы привязать карту. У нового аккаунта Railway обычно требует карту даже на trial/hobby, хотя с неё могут ничего не списывать. Если карты нет — используйте Hugging Face Spaces ниже.

1. Зарегистрируйтесь на [railway.app](https://railway.app) и создайте проект из GitHub-репозитория.
2. Builder: Dockerfile (в репозитории есть `Dockerfile` и `railway.toml`).
3. Variables:

   | Имя | Значение |
   | --- | --- |
   | `SECRET_KEY` | длинная случайная строка |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `*` или ваш домен Railway |
   | `CSRF_TRUSTED_ORIGINS` | `https://<ваш-сервис>.up.railway.app` |
   | `DB_ENGINE` | `sqlite` |
   | `SQLITE_PATH` | `/app/data/db.sqlite3` |
   | `YANDEX_MAPS_API_KEY` | по желанию |

4. Добавьте volume на `/app/data`, иначе SQLite сотрётся при редеплое.
5. Порт берётся из `$PORT` автоматически через `scripts/entrypoint.py`.
6. После деплоя откройте публичный URL. Каталог подтянется из фикстуры при первом старте.

## Hugging Face Spaces (без карты)

1. [huggingface.co](https://huggingface.co) → New Space → SDK **Docker**.
2. Variables как в таблице выше, `CSRF_TRUSTED_ORIGINS=https://<логин>-altay-engineering.hf.space`.
3. В README Space оставьте YAML с `sdk: docker` и `app_port: 7860`.
4. Залейте код и дождитесь сборки.

## PythonAnywhere

Beginner без карты, но жёсткий лимит CPU (~100 с/сутки) и 512 МБ диска. Для каталога с картинками неудобно. Инструкция: Manual configuration + WSGI на `website.wsgi`, SQLite, WhiteNoise.

## Локально через Docker

```bash
docker compose up --build
```

http://localhost:8000
