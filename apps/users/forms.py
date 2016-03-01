# (c) Crown Owned Copyright, 2016. Dstl.
# apps/users/forms.py
from django import forms
from .models import User


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['slug', ]


class UserUpdateProfile(forms.ModelForm):

    class Meta:
        model = User
        fields = [
                    'username',
                    'bestWayToFind',
                    'bestWayToContact',
                    'phone',
                    'email'
                ]
