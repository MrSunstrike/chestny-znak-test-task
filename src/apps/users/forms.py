from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Пароль",
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ("username", "email", "first_name", "last_name"):
            self.fields[field_name].required = True

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        user = self.instance.__class__(
            username=self.cleaned_data.get("username", ""),
            email=self.cleaned_data.get("email", ""),
            first_name=self.cleaned_data.get("first_name", ""),
            last_name=self.cleaned_data.get("last_name", ""),
        )
        validate_password(password, user)
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
