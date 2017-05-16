from django import forms
from django.contrib.auth.models import User

from .models import Profile

class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(label='Email', max_length='130', required=True, widget=forms.TextInput())
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email',]

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords dont match')
        return cd['password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(u'Email addresses must be unique.')
        return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['country_code', 'phone_number']

class VerifySMSForm(forms.Form):
    sms_password = forms.IntegerField()

    class Meta:
        fields = ['sms_password']