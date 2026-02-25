from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

BOROUGH_CHOICES = [
    ('', 'Select your borough (optional)'),
    ('Manhattan', 'Manhattan'),
    ('Brooklyn', 'Brooklyn'),
    ('Queens', 'Queens'),
    ('Bronx', 'Bronx'),
    ('Staten Island', 'Staten Island'),
]


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email address',
            'class': 'form-input',
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'First name',
            'class': 'form-input',
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name',
            'class': 'form-input',
        })
    )
    borough = forms.ChoiceField(
        choices=BOROUGH_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'borough', 'password1', 'password2'
        )
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Username',
                'class': 'form-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password',
            'class': 'form-input',
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm password',
            'class': 'form-input',
        })
        # Remove help text for cleaner UI
        for field in self.fields.values():
            field.help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.borough = self.cleaned_data.get('borough', '')
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-input',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-input',
        })
    )
