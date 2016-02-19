from django import forms
from .models import Link


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ('name', 'description', 'destination', 'categories',
                  'is_external',)
