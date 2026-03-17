from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.users.models import User
from apps.users.forms import UserRegistrationForm

User = get_user_model()


class UserRegistrationFormTest(TestCase):
    """
    Тесты для формы регистрации пользователя.
    """

    def test_form_valid_data(self):
        """
        Тест формы с корректными данными.
        """

        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "complexpassword123!",
            "password2": "complexpassword123!",
        }

        form = UserRegistrationForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_form_missing_required_fields(self):
        """
        Тест формы с отсутствующими обязательными полями.
        """

        form_data = {
            "email": "test@example.com",
            "password1": "complexpassword123!",
            "password2": "complexpassword123!",
        }

        form = UserRegistrationForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_form_passwords_not_matching(self):
        """
        Тест формы с несовпадающими паролями.
        """

        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "complexpassword123!",
            "password2": "differentpassword456!",
        }

        form = UserRegistrationForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
        self.assertEqual(form.errors["password2"], ["Пароли не совпадают."])

    def test_form_password_validation(self):
        """
        Тест валидации пароля.
        """

        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "123",
            "password2": "123",
        }

        form = UserRegistrationForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors)

    def test_form_save_method(self):
        """
        Тест метода сохранения формы.
        """

        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "complexpassword123!",
            "password2": "complexpassword123!",
        }

        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("complexpassword123!"))
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")

    def test_clean_password1_method(self):
        """
        Тест метода проверки первого пароля.
        """

        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "complexpassword123!",
            "password2": "complexpassword123!",
        }

        form = UserRegistrationForm(data=form_data)

        self.assertTrue(form.is_valid())

        form.full_clean()
        cleaned_password = form.clean_password1()

        self.assertEqual(cleaned_password, "complexpassword123!")

    def test_clean_password2_method_matching(self):
        """
        Тест метода проверки второго пароля с совпадающими паролями.
        """

        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "complexpassword123!",
            "password2": "complexpassword123!",
        }

        form = UserRegistrationForm(data=form_data)

        self.assertTrue(form.is_valid())

        form.full_clean()
        cleaned_password = form.clean_password2()

        self.assertEqual(cleaned_password, "complexpassword123!")

    def test_clean_password2_method_not_matching(self):
        """
        Тест метода очистки второго пароля с несовпадающими паролями.
        """

        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "complexpassword123!",
            "password2": "differentpassword456!",
        }

        form = UserRegistrationForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
        self.assertIn("Пароли не совпадают.", form.errors["password2"])


class UserViewTest(TestCase):
    """
    Тесты для представлений пользователей.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

    def test_user_register_view_get(self):
        """
        Тест GET запроса к странице регистрации.
        """

        response = self.client.get(reverse("users:register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

    def test_user_register_view_post_success(self):
        """
        Тест успешной регистрации пользователя.
        """

        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password1": "complexpassword123!",
            "password2": "complexpassword123!",
        }

        response = self.client.post(reverse("users:register"), form_data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_register_view_post_invalid_data(self):
        """
        Тест регистрации пользователя с невалидными данными.
        """

        form_data = {
            "username": "",
            "email": "invalid-email",
            "first_name": "New",
            "last_name": "User",
            "password1": "123",
            "password2": "456",
        }

        response = self.client.post(reverse("users:register"), form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

        form = response.context["form"]

        self.assertFalse(form.is_valid())

    def test_user_login_view_get(self):
        """
        Тест GET запроса к странице входа.
        """

        response = self.client.get(reverse("users:login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_user_login_view_post_success(self):
        """
        Тест успешного входа пользователя.
        """

        login_data = {"username": "testuser", "password": "testpass123"}

        response = self.client.post(reverse("users:login"), login_data)

        self.assertEqual(response.status_code, 302)

    def test_user_login_view_post_invalid_credentials(self):
        """
        Тест входа пользователя с неверными учетными данными.
        """

        login_data = {"username": "testuser", "password": "wrongpassword"}

        response = self.client.post(reverse("users:login"), login_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

        form = response.context["form"]

        self.assertFalse(form.is_valid())

    def test_user_logout_view(self):
        """
        Тест выхода пользователя.
        """

        login_data = {"username": "testuser", "password": "testpass123"}
        self.client.post(reverse("users:login"), login_data)

        response = self.client.get(reverse("orders:list"))

        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("users:logout"))

        self.assertEqual(response.status_code, 302)

    def test_login_redirects_authenticated_user(self):
        """
        Тест, что аутентифицированный пользователь перенаправляется со страницы входа.
        """

        login_data = {"username": "testuser", "password": "testpass123"}
        self.client.post(reverse("users:login"), login_data)

        response = self.client.get(reverse("users:login"))

        self.assertEqual(response.status_code, 302)
