from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from users.models import User

from api_yamdb.settings import AUTH_CONF_CODE_MAXLENGTH, EMAIL_CONFIRMATION


def create_and_send_code(username):
    user = get_object_or_404(User, username=username)
    code = get_random_string(length=AUTH_CONF_CODE_MAXLENGTH)
    user.confirmation_code = code
    user.save()
    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения для получения токена: {code}.',
        EMAIL_CONFIRMATION,
        [f'{user.email}'],
        fail_silently=False,
    )
