import autocomplete_light
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.safestring import mark_safe
from .models import RegistrationModel


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    agree_to_term = forms.BooleanField(required=True,
                                       label=mark_safe('I agree to the <a href="/terms-of-use">Terms of Service</a>'))
    organization = forms.CharField(widget=autocomplete_light.TextWidget('OrganizationAutocomplete'))
    password = forms.CharField(widget=forms.PasswordInput())
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta:
        model = RegistrationModel
        widget = autocomplete_light.get_widgets_dict(RegistrationModel)
        fields = [
            'position_title',
            'hear_mediathread_from',
            'subscribe_to_newsletter']


class InviteStudentsForm(forms.Form):
    email_from = forms.EmailField(
        label="From"
    )
    student_emails = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        label="To"
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 20})
    )

    def __init__(self, *args, **kwargs):
        super(InviteStudentsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        submit_button = Submit('submit', 'Invite students')
        submit_button.field_classes = 'btn'
        self.helper.add_input(submit_button)

    def clean_student_emails(self):
        data = self.cleaned_data['student_emails'].splitlines()
        emails = []
        for email in data:
            if "@" in email:
                emails.append(email.strip())
            else:
                raise forms.ValidationError("Error in an email address")
        return emails
