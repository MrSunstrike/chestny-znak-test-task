from django import forms

from apps.orders.models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        volume_type = cleaned_data.get("volume_type")
        errors: dict[str, str] = {}

        self._normalize_by_volume_type(cleaned_data, volume_type)

        if volume_type == Order.OrderVolumeType.SINGLE:
            errors.update(self._validate_single(cleaned_data))

        elif volume_type == Order.OrderVolumeType.MULTIPLE:
            errors.update(self._validate_multiple(cleaned_data))

        elif volume_type is not None:
            errors["volume_type"] = "Некорректный тип объема заказа."

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data

    def _normalize_by_volume_type(self, cleaned_data: dict, volume_type: str | None) -> None:
        if volume_type == Order.OrderVolumeType.SINGLE:
            cleaned_data["quantity"] = 1
            cleaned_data["document"] = False
            self._mark_changed("quantity", "document")

        elif volume_type == Order.OrderVolumeType.MULTIPLE:
            cleaned_data["description"] = ""
            self._mark_changed("description")

    @staticmethod
    def _validate_single(cleaned_data: dict) -> dict[str, str]:
        errors: dict[str, str] = {}

        description = (cleaned_data.get("description") or "").strip()
        document = cleaned_data.get("document")
        quantity = cleaned_data.get("quantity")

        if not description:
            errors["description"] = "Для единичного заказа необходимо указать описание."

        if document:
            errors["document"] = "Для единичного заказа документ не требуется."

        if quantity != 1:
            errors["quantity"] = "Для единичного заказа количество должно быть равно 1."

        return errors

    @staticmethod
    def _validate_multiple(cleaned_data: dict) -> dict[str, str]:
        errors: dict[str, str] = {}

        description = (cleaned_data.get("description") or "").strip()
        document = cleaned_data.get("document")
        quantity = cleaned_data.get("quantity")

        if description:
            errors["description"] = "Для множественного заказа описание не должно быть указано."

        if not document:
            errors["document"] = "Для множественного заказа необходимо прикрепить документ."

        if quantity is None or quantity <= 1:
            errors["quantity"] = "Для множественного заказа количество должно быть больше 1."

        return errors

    def _mark_changed(self, *fields: str) -> None:
        for field in fields:
            if field not in self.changed_data:
                self.changed_data.append(field)


class UserOrderForm(OrderForm):
    class Meta(OrderForm.Meta):
        fields = (
            "name",
            "volume_type",
            "quantity",
            "description",
            "document",
        )
