# (c) Crown Owned Copyright, 2016. Dstl.

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.text import slugify

from .models import User


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        # If one field gets autocompleted but not the other, our 'neither
        # password or both password' validation will be triggered.
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = User
        fields = ('userid',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        if self.cleaned_data['password2']:
            user.set_password(self.cleaned_data['password2'])
        else:
            user.set_unusable_password()
        user.slug = slugify(user.userid)
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            'userid',
            'password',
            'is_active',
            'is_staff',
            'is_superuser',
            'best_way_to_find',
            'best_way_to_contact',
            'phone',
            'email',
            'teams',
        )

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('userid', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser',)
    fieldsets = (
        (None, {'fields': ('userid', 'password')}),
        ('Personal info', {'fields': (
            'name', 'best_way_to_find', 'best_way_to_contact', 'email', 'phone'
        )}),
        ('Teams', {'fields': ('teams',)}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('userid', 'password1', 'password2')
        }),
    )
    search_fields = ('userid',)
    ordering = ('userid',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
