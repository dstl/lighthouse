# (c) Crown Owned Copyright, 2016. Dstl.
# apps/organisations/forms.py
from django import forms
from .models import Organisation


class OrganisationForm(forms.ModelForm):

    class Meta:
        model = Organisation
        fields = ['name', ]
