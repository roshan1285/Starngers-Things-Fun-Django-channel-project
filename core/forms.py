from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email'] # Password is included automatically by UserCreationForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Loop through all fields and add a modern CSS class
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'modern-input',
                'placeholder': f'Enter your {field}'
            })

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Loop through all fields and add a modern CSS class
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'modern-input',
                'placeholder': f'Enter your {field}'
            })