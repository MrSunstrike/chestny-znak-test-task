from django.contrib.auth import get_user_model
from django.db import models

from apps.common.models import TimeStampedModel
from config.constants import ENUM_TEXT_MAX_LENGTH, LONG_TEXT_MAX_LENGTH, SHORT_TEXT_MAX_LENGTH

User = get_user_model()


class Order(TimeStampedModel):
    class OrderStatus(models.TextChoices):
        CREATED = "created", "Создан"
        PROCESSING = "processing", "Обрабатывается"
        ASSEMBLING = "assembling", "Собирается"
        DELIVERING = "delivering", "Доставляется"
        READY = "ready", "Готов"

    class OrderVolumeType(models.TextChoices):
        SINGLE = "single", "Единичный"
        MULTIPLE = "multiple", "Множественный"

    user = models.ForeignKey(
        verbose_name="Пользователь",
        to=User,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    name = models.CharField(
        verbose_name="Наименование",
        max_length=SHORT_TEXT_MAX_LENGTH,
    )
    volume_type = models.CharField(
        verbose_name="Тип объема заказа",
        max_length=ENUM_TEXT_MAX_LENGTH,
        choices=OrderVolumeType.choices,
    )
    description = models.TextField(
        verbose_name="Описание",
        max_length=LONG_TEXT_MAX_LENGTH,
        blank=True,
    )
    document = models.FileField(
        verbose_name="Документ",
        upload_to="orders/%Y/%m/%d/",
        blank=True,
        null=True,
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Количество",
        default=1,
        help_text="Указывается для множественного заказа",
    )
    status = models.CharField(
        verbose_name="Статус",
        max_length=ENUM_TEXT_MAX_LENGTH,
        choices=OrderStatus.choices,
        default=OrderStatus.CREATED,
    )
    ready_at = models.DateTimeField(
        verbose_name="Дата готовности",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Заказ #{self.pk} — {self.name}"
