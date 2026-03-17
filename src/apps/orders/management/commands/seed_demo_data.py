from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.orders.models import Order

User = get_user_model()


class Command(BaseCommand):
    help = "Cоздает демо-данные и суперпользователя admin/admin"

    def handle(self, *args, **options):
        admin_user, admin_created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.set_password("admin")
        admin_user.save()

        user, user_created = User.objects.update_or_create(
            username="demo_user",
            defaults={
                "email": "demo_user@example.com",
                "first_name": "Demo",
                "last_name": "User",
                "is_staff": False,
                "is_superuser": False,
                "is_active": True,
            },
        )
        user.set_password("demo_user")
        user.save()

        staff, staff_created = User.objects.update_or_create(
            username="demo_staff",
            defaults={
                "email": "demo_staff@example.com",
                "first_name": "Demo",
                "last_name": "Staff",
                "is_staff": True,
                "is_superuser": False,
                "is_active": True,
            },
        )
        staff.set_password("demo_staff")
        staff.save()

        demo_orders = [
            {
                "user": user,
                "name": "Единичный заказ demo_user",
                "volume_type": Order.OrderVolumeType.SINGLE,
                "description": "Тестовое описание для единичного заказа",
                "quantity": 1,
                "status": Order.OrderStatus.CREATED,
                "ready_at": None,
            },
            {
                "user": user,
                "name": "Готовый заказ demo_user",
                "volume_type": Order.OrderVolumeType.SINGLE,
                "description": "Заказ для проверки статуса READY",
                "quantity": 1,
                "status": Order.OrderStatus.READY,
                "ready_at": timezone.now(),
            },
            {
                "user": staff,
                "name": "Множественный заказ demo_staff",
                "volume_type": Order.OrderVolumeType.MULTIPLE,
                "description": "",
                "quantity": 5,
                "status": Order.OrderStatus.PROCESSING,
                "ready_at": None,
            },
        ]

        created_orders = 0
        updated_orders = 0
        for payload in demo_orders:
            _, created = Order.objects.update_or_create(
                user=payload["user"],
                name=payload["name"],
                defaults={
                    "volume_type": payload["volume_type"],
                    "description": payload["description"],
                    "quantity": payload["quantity"],
                    "status": payload["status"],
                    "ready_at": payload["ready_at"],
                },
            )
            if created:
                created_orders += 1
            else:
                updated_orders += 1

        self.stdout.write(self.style.SUCCESS("Готово: демо-данные актуализированы."))
        self.stdout.write(
            "Users: "
            f"admin={'created' if admin_created else 'updated'}, "
            f"demo_user={'created' if user_created else 'updated'}, "
            f"demo_staff={'created' if staff_created else 'updated'}"
        )
        self.stdout.write(f"Orders: created={created_orders}, updated={updated_orders}")
        self.stdout.write("Admin credentials: admin/admin")
