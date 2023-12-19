from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


from django.contrib.auth.forms import AuthenticationForm

# If you need to customize the form, you can extend AuthenticationForm
class LoginForm(AuthenticationForm):
    pass
    # Add any additional fields or validations if needed


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", 'password2']