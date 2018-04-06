from django import forms
from .models import ExtendedUser


class LoginForm(forms.ModelForm):
    class Meta:
        model = ExtendedUser
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'username', }),
            'password': forms.PasswordInput(attrs={'class': "form-control", 'placeholder': 'password', }),
        }


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = ExtendedUser
        fields = ['first_name', 'last_name', 'username', 'password', 'email', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'username', }),
            'password': forms.PasswordInput(attrs={'class': "form-control", 'placeholder': 'password',
                                                   'style': "margin-bottom: -1px;",
                                                   }),
            'first_name': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'first_name', }),
            'last_name': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'last_name', }),
            'email': forms.EmailInput(attrs={'class': "form-control", 'placeholder': 'email', }),
            'avatar': forms.FileInput(attrs={'class': 'form-control', }),
        }


class EditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False

    class Meta:
        model = ExtendedUser
        fields = ['first_name', 'last_name', 'username', 'password', 'email', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'username', }),
            'password': forms.PasswordInput(attrs={'class': "form-control", 'placeholder': 'password',
                                                   'style': "margin-bottom: -1px;",
                                                   }),
            'first_name': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'first_name', }),
            'last_name': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'last_name', }),
            'email': forms.EmailInput(attrs={'class': "form-control", 'placeholder': 'email', }),
            'avatar': forms.FileInput(attrs={'class': 'form-control', }),
        }

