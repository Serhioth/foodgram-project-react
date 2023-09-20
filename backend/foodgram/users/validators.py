import re

from django.contrib.auth import get_user_model

User = get_user_model()


def check_username(username):
    """
    Проверка, что имя пользователя != me
    и соответствует regex шаблону
    """
    if username.lower() == 'me':
        return False
    pattern = r'^[\w.@+-]+'
    if not re.findall(pattern, username):
        return False
    return True


def check_user_is_not_registred(username, email):
    """
    Проверка, что пользователь не пытается зарегистрироваться,
    с уже занятыми данными
    """
    if User.objects.filter(
        email=email,
        username=username
    ).exists():
        return True

    if User.objects.filter(
        username=username
    ).exists():
        return False
    if User.objects.filter(
        email=email
    ).exists():
        return False
    return True
