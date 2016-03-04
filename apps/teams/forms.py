# (c) Crown Owned Copyright, 2016. Dstl.
# apps/teams/forms.py
from django import forms
from .models import Team
from apps.organisations.models import Organisation


class TeamForm(forms.ModelForm):

    error_both_fields = "You can't select an existing organisation and "
    error_both_fields += "create a new one at the same time."

    error_neither_field = "You must select an existing organisation or "
    error_neither_field += "create a new one."

    #   We need an additional free text field, if the user wants to
    #   join the team to a new undefined organisation.
    #   TODO: Somehow pull this from the Organisation model instead?
    new_organisation = forms.CharField(
        max_length=256,
        label='Or add a new organisation',
        required=False,
    )

    #   Include the extra new_organisation field on the form
    class Meta:
        model = Team
        fields = ['name', 'organisation', 'new_organisation']

    #   For the moment we have to overide the save method, to make it
    #   use the *cleaned_data* rather than the submitted data from the
    #   form.
    def save(self, force_insert=False, force_update=False, commit=True):

        new_team = Team()
        new_team.name = self.cleaned_data['name']
        new_team.organisation = self.cleaned_data['organisation']
        new_team.save()
        return new_team

    #   We have to override the validation, because it's ok for the user
    #   to have *NOT* selected an organisation from the dropdown, and the
    #   default validation will throw an error in this case.
    def is_valid(self):
        valid = super(TeamForm, self).is_valid()

        if 'organisation' in self._errors.keys():
            req_err = 'This field is required.' in self._errors['organisation']
            neit_err = self.error_neither_field in self._errors['organisation']
            both_err = self.error_both_fields in self._errors['organisation']

            # This means we're good because the new org is in there
            if req_err and not neit_err and not both_err:
                self._errors['organisation'] = []
                if len(self._errors.keys()) == 1:
                    self._errors = {}
                    valid = True
            # This means we just need to show the neither error
            elif neit_err:
                self._errors['organisation'] = [self.error_neither_field]
            # This means we just need to show the both error
            elif both_err:
                self._errors['organisation'] = [self.error_both_fields]

        return valid

    #   Here we have the chance to do some cleaning up, because we are
    #   allowing the *not* passing in of an organisation to pass validation
    #   we want to do a bit if cleaning up and extra validation here.
    def clean(self):
        cleaned_data = super(TeamForm, self).clean()

        #   We've been passed both org & new_org, *sigh*
        if ('organisation' in cleaned_data and
                cleaned_data['new_organisation'] != ''):
                    raise forms.ValidationError({
                            "organisation": [self.error_both_fields]
                        }
                    )

        #   We've been passed neither, *double sigh*
        if ('organisation' not in cleaned_data and
                cleaned_data['new_organisation'] == ''):
                    raise forms.ValidationError({
                            "organisation": [self.error_neither_field]
                        }
                    )

        #   We've been passed a new organisation
        if ('organisation' not in cleaned_data and
                cleaned_data['new_organisation'] != ''):

            #   Check if the team name already exists
            t_n = cleaned_data.get('name')
            check_team = Team.objects.filter(name=t_n).exists()

            #   If it doesn't then we carry on dealing with the new org
            if check_team is False:

                #   Grab the new org name
                o_n = cleaned_data.get('new_organisation')

                #   See if it exists
                check_org = \
                    Organisation.objects.filter(name=o_n).exists()

                #   If it does, then we just grab it, otherwise create it
                if check_org is True:
                    new_organisation = Organisation.objects.get(name=o_n)
                else:
                    new_organisation = Organisation()
                    new_organisation.name = cleaned_data['new_organisation']
                    new_organisation.save()

                #   put the record into the organisation field, which *should*
                #   contain a valid organisaiton record
                cleaned_data['organisation'] = new_organisation

        #   Just to be neat & tidy, remove the new_organisation field
        del cleaned_data['new_organisation']
        return cleaned_data
