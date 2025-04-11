import os
import django
from decouple import config
from django.core.mail import send_mail

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
django.setup()

print("EMAIL_HOST_USER:", config('EMAIL_HOST_USER'))
print("EMAIL_HOST_PASSWORD:", config('EMAIL_HOST_PASSWORD'))

send_mail(
    'Тестовое письмо',
    'Это тестовое письмо от Django.',
    'alexzhiryakov17@mail.ru',
    ['alexzhiryakov17@mail.ru'],
    fail_silently=False,
)