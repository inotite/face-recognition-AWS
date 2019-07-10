from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe


class UserCreationForm1(UserCreationForm):
    username = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=True, label="Full Name")

    class Meta:
        model = User
        fields = ("first_name", "username", "password1", "password2")
