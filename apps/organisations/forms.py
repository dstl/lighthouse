# apps/organisations/forms.py
from django import forms
from .models import Organisation


class OrganisationForm(forms.ModelForm):

    class Meta:
        model = Organisation
        fields = ['name', ]
