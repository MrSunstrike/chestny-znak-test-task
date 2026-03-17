from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import FormView

from apps.users.forms import UserRegistrationForm


class UserLoginView(LoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True


class UserRegisterView(FormView):
    template_name = "users/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    pass
