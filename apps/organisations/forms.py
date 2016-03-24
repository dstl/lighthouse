# (c) Crown Owned Copyright, 2016. Dstl.

from django import forms

from .models import Organisation


class OrganisationForm(forms.ModelForm):

    class Meta:
        model = Organisation
        fields = ['name', ]
