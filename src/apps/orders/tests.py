from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.admin import AdminSite
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
import json

from apps.orders.models import Order
from apps.orders.forms import OrderForm, UserOrderForm
from apps.orders.admin import OrderAdmin
from apps.users.models import User

User = get_user_model()


class OrderFormTest(TestCase):
    """
    Тесты для форм заказа.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.test_document = SimpleUploadedFile(
            name="test_document.txt", content=b"Here is some mock content for the file.", content_type="text/plain"
        )

    def test_order_form_single_validation_success(self):
        """
        Тест валидации формы для единичного заказа.
        """

        form_data = {
            "user": self.user.id,
            "name": "Test Order",
            "volume_type": Order.OrderVolumeType.SINGLE,
            "description": "Test description",
            "quantity": 1,
            "document": False,
            "status": Order.OrderStatus.CREATED,
        }

        form = OrderForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_order_form_single_validation_missing_description(self):
        """
        Тест валидации формы для единичного заказа без описания.
        """

        form_data = {
            "user": self.user.id,
            "name": "Test Order",
            "volume_type": Order.OrderVolumeType.SINGLE,
            "description": "",
            "quantity": 1,
            "document": False,
            "status": Order.OrderStatus.CREATED,
        }

        form = OrderForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)
        self.assertEqual(form.errors["description"][0], "Для единичного заказа необходимо указать описание.")

    def test_order_form_single_validation_with_document(self):
        """
        Тест валидации формы для единичного заказа с документом.
        """

        form_data = {
            "user": self.user.id,
            "name": "Test Order",
            "volume_type": Order.OrderVolumeType.SINGLE,
            "description": "Test description",
            "quantity": 1,
            "document": True,
            "status": Order.OrderStatus.CREATED,
        }

        form = OrderForm(data=form_data, files={"document": self.test_document})

        self.assertTrue(form.is_valid())

    def test_order_form_single_validation_wrong_quantity(self):
        """
        Тест валидации формы для единичного заказа с неправильным количеством.
        """

        form_data = {
            "user": self.user.id,
            "name": "Test Order",
            "volume_type": Order.OrderVolumeType.SINGLE,
            "description": "Test description",
            "quantity": 5,
            "document": False,
            "status": Order.OrderStatus.CREATED,
        }

        form = OrderForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_order_form_multiple_validation_success(self):
        """
        Тест валидации формы для множественного заказа.
        """

        form_data = {
            "user": self.user.id,
            "name": "Test Order",
            "volume_type": Order.OrderVolumeType.MULTIPLE,
            "quantity": 5,
            "document": self.test_document,
            "status": Order.OrderStatus.CREATED,
        }

        form = OrderForm(data=form_data, files={"document": self.test_document})

        self.assertTrue(form.is_valid())

    def test_order_form_multiple_validation_with_description(self):
        """
        Тест валидации формы для множественного заказа с описанием.
        """

        form_data = {
            "user": self.user.id,
            "name": "Test Order",
            "volume_type": Order.OrderVolumeType.MULTIPLE,
            "description": "Test description",
            "quantity": 5,
            "document": True,
            "status": Order.OrderStatus.CREATED,
        }

        form = OrderForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("document", form.errors)
        self.assertIn("множественного", form.errors["document"][0].lower())

    def test_order_form_multiple_validation_without_document(self):
        """
        Тест валидации формы для множественного заказа без документа.
        """

        form_data = {
            "user": self.user.id,
            "name": "Test Order",
            "volume_type": Order.OrderVolumeType.MULTIPLE,
            "quantity": 5,
            "document": False,
            "status": Order.OrderStatus.CREATED,
        }

        form = OrderForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("document", form.errors)
        self.assertEqual(form.errors["document"][0], "Для множественного заказа необходимо прикрепить документ.")

    def test_order_form_multiple_validation_wrong_quantity(self):
        """
        Тест валидации формы для множественного заказа с неправильным количеством.
        """

        form_data = {
            "user": self.user.id,
            "name": "Test Order",
            "volume_type": Order.OrderVolumeType.MULTIPLE,
            "quantity": 1,
            "document": True,
            "status": Order.OrderStatus.CREATED,
        }

        form = OrderForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)
        self.assertEqual(form.errors["quantity"][0], "Для множественного заказа количество должно быть больше 1.")

    def test_order_form_invalid_volume_type(self):
        """
        Тест валидации формы с неправильным типом объема.
        """

        form_data = {
            "user": self.user.id,
            "name": "Test Order",
            "volume_type": "invalid_type",
            "description": "Test description",
            "quantity": 1,
            "document": False,
            "status": Order.OrderStatus.CREATED,
        }

        form = OrderForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("volume_type", form.errors)
        self.assertIn("invalid_type", form.errors["volume_type"][0])

    def test_user_order_form_fields(self):
        """
        Тест полей формы для пользователей.
        """

        form = UserOrderForm()
        expected_fields = {"name", "volume_type", "quantity", "description", "document"}
        actual_fields = set(form.fields.keys())

        self.assertEqual(expected_fields, actual_fields)

    def test_form_normalization_single_type(self):
        """
        Тест нормализации данных формы для единичного типа.
        """

        form_data = {
            "user": self.user.id,
            "name": "Test Order",
            "volume_type": Order.OrderVolumeType.SINGLE,
            "description": "Test description",
            "quantity": 5,
            "document": True,
            "status": Order.OrderStatus.CREATED,
        }

        form = OrderForm(data=form_data, files={"document": self.test_document})

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["quantity"], 1)
        self.assertFalse(form.cleaned_data["document"])


class OrderAdminTest(TestCase):
    """Тесты для административного интерфейса заказов"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.staff_user = User.objects.create_user(
            username="staffuser", email="staff@example.com", password="testpass123", is_staff=True
        )
        self.order = Order.objects.create(
            user=self.user,
            name="Test Order",
            volume_type=Order.OrderVolumeType.SINGLE,
            description="Test description",
            quantity=1,
            status=Order.OrderStatus.CREATED,
        )
        self.admin = OrderAdmin(Order, AdminSite())

    def test_fieldsets(self):
        """
        Тест наборов полей при просмотре существующего заказа.
        """

        self.assertEqual(len(self.admin.fieldsets), 3)

        user_info_fieldset = self.admin.fieldsets[0]
        self.assertEqual(user_info_fieldset[0], "Информация о пользователе")
        self.assertIn("user", user_info_fieldset[1]["fields"])

        order_info_fieldset = self.admin.fieldsets[1]
        self.assertEqual(order_info_fieldset[0], "Информация о заказе")
        self.assertIn("name", order_info_fieldset[1]["fields"])

        status_fieldset = self.admin.fieldsets[2]
        self.assertEqual(status_fieldset[0], "Статус заказа")
        self.assertIn(("status", "ready_at"), status_fieldset[1]["fields"])

    def test_get_fieldsets_create(self):
        """
        Тест получения наборов полей при создании нового заказа.
        """

        request = None
        fieldsets = self.admin.get_fieldsets(request, obj=None)

        self.assertEqual(len(fieldsets), 1)
        self.assertEqual(fieldsets[0][0], "Создание заявки")

    def test_save_model_sets_ready_at(self):
        """
        Тест сохранения модели устанавливает дату готовности.
        """

        order = Order.objects.create(
            user=self.user,
            name="Another Order",
            volume_type=Order.OrderVolumeType.SINGLE,
            description="Test description",
            quantity=1,
            status=Order.OrderStatus.CREATED,
            ready_at=None,
        )

        order.status = Order.OrderStatus.READY

        request = None
        form = OrderForm(instance=order)

        self.admin.save_model(request, order, form, True)
        order.refresh_from_db()

        self.assertIsNotNone(order.ready_at)

    def test_save_model_clears_ready_at(self):
        """
        Тест сохранения модели очищает дату готовности если статус не READY.
        """

        now = timezone.now()
        order = Order.objects.create(
            user=self.user,
            name="Another Order",
            volume_type=Order.OrderVolumeType.SINGLE,
            description="Test description",
            quantity=1,
            status=Order.OrderStatus.READY,
            ready_at=now,
        )

        order.status = Order.OrderStatus.PROCESSING

        request = None  # Mock request
        form = OrderForm(instance=order)

        self.admin.save_model(request, order, form, True)
        order.refresh_from_db()

        self.assertIsNone(order.ready_at)


class OrderViewTest(TestCase):
    """
    Тесты для представлений заказов.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.staff_user = User.objects.create_user(
            username="staffuser", email="staff@example.com", password="testpass123", is_staff=True
        )
        self.order = Order.objects.create(
            user=self.user,
            name="Test Order",
            volume_type=Order.OrderVolumeType.SINGLE,
            description="Test description",
            quantity=1,
            status=Order.OrderStatus.CREATED,
        )

    def test_order_list_view_requires_login(self):
        """
        Тест что список заказов требует авторизации.
        """

        response = self.client.get(reverse("orders:list"))

        self.assertEqual(response.status_code, 302)

    def test_order_list_view_authenticated(self):
        """
        Тест списка заказов для аутентифицированного пользователя.
        """

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("orders:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Order")

    def test_order_list_view_shows_only_user_orders(self):
        """
        Тест что список заказов показывает только заказы текущего пользователя.
        """

        other_user = User.objects.create_user(username="otheruser", email="other@example.com", password="testpass123")
        Order.objects.create(
            user=other_user,
            name="Other User Order",
            volume_type=Order.OrderVolumeType.SINGLE,
            description="Test description",
            quantity=1,
            status=Order.OrderStatus.CREATED,
        )

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("orders:list"))

        self.assertContains(response, "Test Order")
        self.assertNotContains(response, "Other User Order")

    def test_order_list_view_staff_sees_all_orders(self):
        """
        Тест что персонал видит все заказы.
        """

        other_user = User.objects.create_user(username="otheruser", email="other@example.com", password="testpass123")
        Order.objects.create(
            user=other_user,
            name="Other User Order",
            volume_type=Order.OrderVolumeType.SINGLE,
            description="Test description",
            quantity=1,
            status=Order.OrderStatus.CREATED,
        )

        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(reverse("orders:list"))

        self.assertContains(response, "Test Order")
        self.assertContains(response, "Other User Order")

    def test_order_list_view_filters_by_status(self):
        """
        Тест фильтрации списка заказов по статусу.
        """

        Order.objects.create(
            user=self.user,
            name="Processing Order",
            volume_type=Order.OrderVolumeType.SINGLE,
            description="Test description",
            quantity=1,
            status=Order.OrderStatus.PROCESSING,
        )

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("orders:list"), {"status": "processing"})

        self.assertContains(response, "Processing Order")
        self.assertNotContains(response, "Test Order")

    def test_order_list_view_filters_by_user_staff(self):
        """
        Тест фильтрации списка заказов по пользователю для персонала.
        """

        other_user = User.objects.create_user(username="otheruser", email="other@example.com", password="testpass123")
        Order.objects.create(
            user=other_user,
            name="Other User Order",
            volume_type=Order.OrderVolumeType.SINGLE,
            description="Test description",
            quantity=1,
            status=Order.OrderStatus.CREATED,
        )

        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(reverse("orders:list"), {"user": str(other_user.id)})

        self.assertContains(response, "Other User Order")
        self.assertNotContains(response, "Test Order")

    def test_order_detail_view_requires_login(self):
        """
        Тест что детали заказа требуют авторизации.
        """

        response = self.client.get(reverse("orders:detail", kwargs={"pk": self.order.pk}))

        self.assertEqual(response.status_code, 302)

    def test_order_detail_view_authenticated(self):
        """
        Тест деталей заказа для аутентифицированного пользователя.
        """

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("orders:detail", kwargs={"pk": self.order.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Order")

    def test_order_detail_view_other_user_access_denied(self):
        """
        Тест что другой пользователь не может получить доступ к чужому заказу.
        """

        other_user = User.objects.create_user(username="otheruser", email="other@example.com", password="testpass123")

        other_order = Order.objects.create(
            user=other_user,
            name="Other User Order",
            volume_type=Order.OrderVolumeType.SINGLE,
            description="Test description",
            quantity=1,
            status=Order.OrderStatus.CREATED,
        )

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("orders:detail", kwargs={"pk": other_order.pk}))

        self.assertEqual(response.status_code, 404)

    def test_order_detail_view_staff_can_access_any_order(self):
        """
        Тест что персонал может получить доступ к любому заказу.
        """

        other_user = User.objects.create_user(username="otheruser", email="other@example.com", password="testpass123")
        other_order = Order.objects.create(
            user=other_user,
            name="Other User Order",
            volume_type=Order.OrderVolumeType.SINGLE,
            description="Test description",
            quantity=1,
            status=Order.OrderStatus.CREATED,
        )

        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(reverse("orders:detail", kwargs={"pk": other_order.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Other User Order")

    def test_order_create_view_requires_login(self):
        """
        Тест что создание заказа требует авторизации.
        """

        response = self.client.get(reverse("orders:create"))

        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_order_create_view_authenticated_get(self):
        """
        Тест формы создания заказа для аутентифицированного пользователя.
        """

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("orders:create"))

        self.assertEqual(response.status_code, 200)

    def test_order_create_view_post_success(self):
        """
        Тест успешного создания заказа.
        """

        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(
            reverse("orders:create"),
            {
                "name": "New Order",
                "volume_type": Order.OrderVolumeType.SINGLE,
                "description": "New order description",
                "quantity": 1,
                "document": "",
            },
        )

        self.assertEqual(response.status_code, 302)

        order = Order.objects.get(name="New Order")

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.description, "New order description")

    def test_users_autocomplete_unauthenticated(self):
        """
        Тест автозаполнения пользователей для неавторизованного пользователя (ручка для фильтра админа).
        """

        response = self.client.get(reverse("orders:users-autocomplete"))

        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_users_autocomplete_non_staff(self):
        """
        Тест автозаполнения пользователей для обычного пользователя (ручка для фильтра админа).
        """

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("orders:users-autocomplete"))

        self.assertEqual(response.status_code, 403)

    def test_users_autocomplete_staff_no_query(self):
        """
        Тест автозаполнения пользователей для админа без запроса (ручка для фильтра админа).
        """

        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(reverse("orders:users-autocomplete"))

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)

        self.assertEqual(data["results"], [])

    def test_users_autocomplete_staff_with_query(self):
        """
        Тест автозаполнения пользователей для персонала с запросом.
        """

        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(reverse("orders:users-autocomplete"), {"q": "test"})

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)

        self.assertGreater(len(data["results"]), 0)

        found_test_user = any(result["id"] == self.user.id for result in data["results"])

        self.assertTrue(found_test_user)
