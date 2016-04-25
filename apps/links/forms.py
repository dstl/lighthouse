# (c) Crown Owned Copyright, 2016. Dstl.

from django import forms
from .models import Link


class LinkUpdateForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = [
            'name', 'description', 'destination', 'is_external', 'categories'
        ]

    def full_clean(self):
        c = super(LinkUpdateForm, self).full_clean()

        if self.instance.pk in [1, 2] and 'destination' in self._errors:
            del self._errors['destination']

        return c
