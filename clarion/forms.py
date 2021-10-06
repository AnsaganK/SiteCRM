from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from clarion.models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'stars']


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1']
