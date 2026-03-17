from django.contrib import admin
from django.db.models import Count, OuterRef, Subquery, Value
from django.utils import timezone

from apps.orders.forms import OrderForm
from apps.orders.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    list_display = (
        "id",
        "name",
        "user",
        "volume_type",
        "quantity",
        "status",
        "ready_at",
        "created_at",
    )
    search_fields = (
        "id",
        "name",
        "description",
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__username",
    )
    list_filter = (
        "status",
        "volume_type",
        "created_at",
        "ready_at",
    )
    list_editable = ("status",)
    autocomplete_fields = ("user",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "user_first_name",
        "user_last_name",
        "user_email",
        "ready_at",
        "orders_count",
    )
    ordering = ("-created_at",)
    fieldsets = (
        (
            "Информация о пользователе",
            {
                "fields": (
                    "user",
                    ("user_first_name", "user_last_name"),
                    "user_email",
                    "orders_count",
                )
            },
        ),
        (
            "Информация о заказе",
            {
                "fields": (
                    "name",
                    "volume_type",
                    "quantity",
                    "description",
                    "document",
                    ("created_at", "updated_at"),
                )
            },
        ),
        ("Статус заказа", {"fields": (("status", "ready_at"),)}),
    )

    def get_fieldsets(self, request, obj=None):
        if obj:
            return super().get_fieldsets(request, obj)

        fieldsets_for_create = (
            (
                "Создание заявки",
                {
                    "fields": (
                        "user",
                        "name",
                        "volume_type",
                        "quantity",
                        "description",
                        "document",
                    )
                },
            ),
        )

        return fieldsets_for_create

    @admin.display(description="Имя")
    def user_first_name(self, obj):
        return obj.user.first_name if obj.user.first_name else "Отсутствует"

    @admin.display(description="Фамилия")
    def user_last_name(self, obj):
        return obj.user.last_name if obj.user.last_name else "Отсутствует"

    @admin.display(description="Электронная почта")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Количество заказов")
    def orders_count(self, obj):
        return obj.orders_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("user")
        return queryset.annotate(
            orders_count=Subquery(
                Order.objects.filter(user_id=OuterRef("user_id"))
                .annotate(tmp=Value(1))
                .values("tmp")
                .annotate(count=Count("id"))
                .values("count")[:1]
            ),
        )

    def save_model(self, request, obj, form, change):
        if obj.status == Order.OrderStatus.READY and obj.ready_at is None:
            obj.ready_at = timezone.now()

        if obj.status != Order.OrderStatus.READY:
            obj.ready_at = None

        super().save_model(request, obj, form, change)

    class Media:
        js = ("admin/js/order_admin.js",)
