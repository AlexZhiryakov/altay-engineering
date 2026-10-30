# 🛠️ Altay Engineering

Pet-проект: каталог сварочного оборудования, труб ПНД и фитингов на Django. Витрина, фильтры, корзина заявок и админка — без реальной оплаты и с вымышленными контактами.

[![CI](https://github.com/AlexZhiryakov/altay-engineering/actions/workflows/ci.yml/badge.svg)](https://github.com/AlexZhiryakov/altay-engineering/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🔗 Живое демо

- Сайт: [altay-engineering.layero.app](https://altay-engineering.layero.app/)
- Админка: [altay-engineering.layero.app/admin/](https://altay-engineering.layero.app/admin/)

---

## 📖 О проекте

Учебный B2B-каталог: категории и карточки товаров, фильтры, корзина и оформление демо-заявки с согласием на обработку ПДн. Заявка сохраняется в БД; при настроенном SMTP можно отправить PDF менеджеру.

На сайте есть юридические страницы (конфиденциальность, условия, cookies, возврат), баннер «это pet-проект» и cookie-баннер. Контакты, адреса и реквизиты вымышленные — только для портфолио.

Стартовый каталог и фото едут с репозиторием (`app/fixtures/catalog.json`, `media/`). На Layero Free диск эфемерный: каталог поднимается при старте, заявки после cold start могут пропасть.

**English:** Portfolio Django catalog for welding equipment, HDPE pipes and fittings. Demo-only storefront with cart, request flow and admin. No real payments; fictional contacts. SQLite by default.

---

## 🛠️ Стек технологий

- **Python 3.11** — язык проекта
- **Django 5.1** — маршруты, ORM, админка, сессии корзины
- **SQLite** — БД по умолчанию (`DB_ENGINE=mysql` — опционально MySQL)
- **Gunicorn + WhiteNoise** — продакшен-сервер и статика
- **Pillow / ReportLab** — изображения и PDF заявок
- **Layero** — деплой (`layero.json`, `entrypoint.py`)

---

## 🚀 Как пользоваться сайтом

1. Откройте [живое демо](https://altay-engineering.layero.app/).
2. На главной — описание pet-проекта, блоки каталога и услуг, карта (если задан `YANDEX_MAPS_API_KEY`).
3. В **Каталоге** откройте категорию → карточку товара → «В корзину».
4. В корзине оформите заявку (имя, телефон, согласие на ПДн).
5. После отправки откроется страница успеха с номером заявки — запись в БД демо-проекта.
6. Заявки смотрите в админке `/admin/` → **Requests** / **Request items**.

---

## ▶️ Быстрый старт

### Локально

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py loaddata catalog
python manage.py createsuperuser
python manage.py runserver
```

Сайт: http://127.0.0.1:8000 · админка: http://127.0.0.1:8000/admin/

В `.env` достаточно `DEBUG` и `SECRET_KEY` для локального демо. Почта и `YANDEX_MAPS_API_KEY` — по желанию.

### Деплой

Пошагово: [docs/DEPLOY.md](docs/DEPLOY.md).

- `layero.json` — runtime `python_web`, старт `python entrypoint.py` (migrate, каталог, collectstatic, gunicorn)
- На Layero задайте `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, при необходимости `YANDEX_MAPS_API_KEY` и `DJANGO_SUPERUSER_*` для админки
- Также возможны Railway (Docker) и Hugging Face Spaces — см. DEPLOY.md

Юридическое и безопасность: [docs/LEGAL_AND_SECURITY.md](docs/LEGAL_AND_SECURITY.md).

---

## 🧪 Тесты и качество

- `python manage.py test` — тесты приложения
- `ruff check .` — линтер
- CI в GitHub Actions: lint + `manage.py check` + tests на каждый push / PR

```powershell
pip install -r requirements-dev.txt
ruff check .
python manage.py test
```

---

## Автор

[AlexZhiryakov](https://github.com/AlexZhiryakov) · `alexzhiryakov17@mail.ru`

Лицензия: [MIT](LICENSE)
