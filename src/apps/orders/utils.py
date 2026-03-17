from django.contrib.auth import get_user_model

User = get_user_model()


def is_staff_or_superuser(user) -> bool:
    """
    Проверка пользователя на администратора.
    """

    return user.is_staff or user.is_superuser


def build_user_label(user: User) -> str:
    """
    Сборка лейбла пользователя.
    """

    full_name = f"{user.last_name} {user.first_name}".strip()

    if full_name:
        return f"{full_name} ({user.username})"

    return f"{user.username} ({user.email})" if user.email else user.username
