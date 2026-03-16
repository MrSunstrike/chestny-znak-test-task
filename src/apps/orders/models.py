from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

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

    def clean(self) -> None:
        errors: dict[str, str] = {}

        description = (self.description or "").strip()

        if self.volume_type == self.OrderVolumeType.SINGLE:
            if not description:
                errors["description"] = "Для единичного заказа необходимо указать описание."

            if self.document:
                errors["document"] = "Для единичного заказа документ не требуется."

            if self.quantity != 1:
                errors["quantity"] = "Для единичного заказа количество должно быть равно 1."

        elif self.volume_type == self.OrderVolumeType.MULTIPLE:
            if description:
                errors["description"] = "Для множественного заказа описание не должно быть указано."

            if not self.document:
                errors["document"] = "Для множественного заказа необходимо прикрепить документ."

            if self.quantity is None or self.quantity <= 1:
                errors["quantity"] = "Для множественного заказа количество должно быть больше 1."

        else:
            errors["volume_type"] = "Некорректный тип объема заказа."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()

        if self.status == self.OrderStatus.READY and self.ready_at is None:
            self.ready_at = timezone.now()

        if self.status != self.OrderStatus.READY:
            self.ready_at = None

        super().save(*args, **kwargs)
