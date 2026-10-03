from django import forms

from .models import ContactSubmission


class ProjectIntakeForm(forms.Form):
    """Project intake. Exactly three fields are required — name, email and
    the message — and the UI labels every field as Required or Optional to
    match (v1 said "all fields except subject are required" while showing no
    markers at all). Everything else only helps us reply better."""

    project_type = forms.ChoiceField(
        label='What are you working on?', choices=ContactSubmission.PROJECT_TYPES, required=False,
        widget=forms.RadioSelect)
    message = forms.CharField(
        label='Tell us about it', max_length=5000,
        help_text='What are you trying to achieve, what exists today, and any deadlines. A few lines is fine.',
        error_messages={'required': 'Tell us a little about the project — a few lines is enough.'})
    budget = forms.ChoiceField(label='Budget', choices=ContactSubmission.BUDGETS, required=False)
    timeline = forms.ChoiceField(label='Timeline', choices=ContactSubmission.TIMELINES, required=False)
    is_urgent = forms.BooleanField(
        label='This is urgent — something is broken in production', required=False,
        help_text='Urgent requests are triaged the same business day.')
    name = forms.CharField(
        label='Your name', max_length=100,
        error_messages={'required': 'Please enter your name.'})
    email = forms.EmailField(
        label='Email', max_length=254,
        error_messages={'required': 'Please enter your email so we can reply.',
                        'invalid': 'That email address doesn’t look right — please check it.'})
    company = forms.CharField(label='Company', max_length=150, required=False)
    # Honeypot: real people never see or fill this (hidden from AT too).
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}))

    REQUIRED_ORDER = ['message', 'name', 'email']

    def clean_message(self):
        msg = self.cleaned_data['message'].strip()
        if len(msg) < 10:
            raise forms.ValidationError('Could you add a little more detail? At least a sentence helps us reply properly.')
        return msg

    @property
    def is_spam(self):
        return bool(self.data.get('website'))


class SubscribeForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        error_messages={'required': 'Enter your email address.',
                        'invalid': 'That email address doesn’t look right.'})
    website = forms.CharField(required=False)
