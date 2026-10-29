# AlexZhiryakov · демо-каталог

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/AlexZhiryakov/altay-engineering/actions/workflows/ci.yml/badge.svg)](https://github.com/AlexZhiryakov/altay-engineering/actions/workflows/ci.yml)

**Pet-проект / портфолио.** Демонстрационный каталог сварочного оборудования, труб ПНД и фитингов. Сайт показывает витрину, фильтры, корзину заявок и админку Django. Это не действующий бизнес и не интернет-магазин: оплата не принимается, контакты и реквизиты вымышленные.

**Live-демо:** после деплоя на [Layero](https://app.layero.ru/) (см. [docs/DEPLOY.md](docs/DEPLOY.md)).

## English

Portfolio Django catalog for HDPE pipes, fittings and welding equipment. Demo-only: no real payments, fictional contacts. SQLite by default. See [docs/DEPLOY.md](docs/DEPLOY.md).

## Возможности

- Каталог с фильтрами и карточками товаров
- Корзина и демо-заявка с согласием на обработку ПДн
- PDF заявки и письмо менеджеру при настроенной почте
- Юридические страницы: конфиденциальность, условия, cookies, возврат
- Баннер «это pet-проект» и информационный cookie-баннер
- Админка Django

## Стек

- Python 3.11, Django 5.1
- **SQLite** по умолчанию (товары, заявки, сессии)
- MySQL опционально через `DB_ENGINE=mysql`
- Pillow, ReportLab, WhiteNoise, Gunicorn

## Где лежат данные

| Что | Где |
| --- | --- |
| Товары, категории, фото-метаданные | таблица SQLite `db.sqlite3` (или MySQL) |
| Файлы фотографий | папка `media/products/` |
| Заявки клиентов | таблицы `app_request`, `app_requestitem` в той же БД |
| Корзина | session cookie Django |
| Секреты | `.env` (не в git) |

Стартовый каталог загружается из `app/fixtures/catalog.json`.

## Запуск локально

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py loaddata catalog
python manage.py createsuperuser
python manage.py runserver
```

Сайт: http://127.0.0.1:8000

## Деплой

Пошагово: [docs/DEPLOY.md](docs/DEPLOY.md).

Кратко:

1. **Layero** — Free без карты, до 5 проектов; конфиг в `layero.json`.
2. **Railway** — Docker, у нового аккаунта часто просят карту.
3. **Hugging Face Spaces** — бесплатно без карты, сайт засыпает без визитов.

## Юридическое и безопасность

См. [docs/LEGAL_AND_SECURITY.md](docs/LEGAL_AND_SECURITY.md).

## Автор

[AlexZhiryakov](https://github.com/AlexZhiryakov)

Контактная почта на сайте: `alexzhiryakov17@mail.ru`.
Письма с PDF заявок уходят только если в `.env` явно заданы SMTP и `ORDER_NOTIFICATION_EMAIL`.

## Лицензия

[MIT](LICENSE)
