import requests
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView, FormView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from authy.api import AuthyApiClient

from .forms import UserRegistrationForm, ProfileForm, VerifySMSForm

# Create your views here.

def get_authy_client():
    return AuthyApiClient(settings.AUTHY_API_KEY)

client = get_authy_client()

@login_required
def dashboard(request):
    return render(
        request,
        'account/dashboard.html',
        {
            'section': 'dashboard',
        }
    )

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save(commit = False)
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            authy_user = client.users.create(
                user_form.cleaned_data['email'],
                profile_form.cleaned_data['phone_number'],
                profile_form.cleaned_data['country_code']
            )
            if authy_user.ok():
                new_user.save()

                user = authenticate(username=user_form.cleaned_data['username'],
                                    password=user_form.cleaned_data['password']
                                )

                new_profile = profile_form.save(commit = False)
                new_profile.user = user
                new_profile.authy_id = authy_user.id
                new_profile.save()
            else:
                errors = authy_user.errors()
                messages.add_message(request, messages.ERROR, errors,get('message'))

            return render(
                request,
                'account/register_done.html',
                {
                    'new_user': new_user
                }
            )
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileForm()
    return render(
        request,
        'account/register.html',
        {
            'user_form': user_form,
            'profile_form': profile_form
        }
    )

class LoginView(FormView):
    template_name = 'registration/login.html'
    form_class = AuthenticationForm
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            messages.add_message(self.request, messages.INFO,
                                "User already logged in")
            return redirect('/')
        else:
            return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        user = authenticate(username=form.cleaned_data['username'], 
                            password=form.cleaned_data['password'])

        if user:
            authy_id = user.profile.authy_id
            api_uri = client.api_uri
            url = '{0}/onetouch/json/users/{1}/approval_requests'.format(api_uri, authy_id)       
            data = {
                'api_key': client.api_key,
                'message': "Request to login to Gizmo app",
                'details[Email': user.email
            }
            response = requests.post(url, data=data)
            json_response = response.json()

            if 'approval_request' in json_response:
                pass
            else:
                """
                Send the verification code with sms 
                """
                sms = client.users.request_sms(authy_id)
                if sms.ok():
                    self.request.session['user_auth_id'] = authy_id
                    return redirect('/verify-sms')
                else:
                    errors = sms.errors()
                    messages.add_message(self.request, messages.ERROR, errors.get('message'))
                    return redirect('/login')

            print('JSON Response:\n', json_response)

class VerifySMS(FormView):
    template_name = 'account/verify-sms.html'
    form_class = VerifySMSForm

    def dispatch(self, request, *args, **kwargs):
        user_auth = self.request.session['user_auth_id']
        if not user_auth:
            return redirect('/')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Use this to add extra context."""
        user_auth = self.request.session['user_auth_id']
        context = super(VerifySMS, self).get_context_data(**kwargs)
        context['user_auth_id'] = user_auth
        context['remove_success_message'] = 0
        return context

    def form_valid(self, form):
        sms_token = str(form.cleaned_data['sms_password'])
        user_auth = self.request.POST['user_auth_id']
        remove_success_message = 0
        if user_auth:
            try:
                verification = client.tokens.verify(user_auth, sms_token)
            except Exception as e:
                messages.add_message(self.request, messages.ERROR, e)
                if e == "Token is invalid. Token was used recently":
                    remove_success_message = 1
                else: 
                    remove_success_message = 0
                return render(
                    self.request,
                    'account/verify-sms.html',
                    {
                        'remove_success_message': remove_success_message,
                        'user_auth_id': user_auth,
                        'form': VerifySMSForm,
                    }
                )
            if verification.ok():
                user = User.objects.get(profile__authy_id=user_auth)
                login(self.request, user)
                return redirect('/')
            else:
                errors = verification.errors()
                messages.add_message(self.request, messages.ERROR, errors.get('message'))
                return render(
                    self.request,
                    'account/verify-sms.html',
                    {
                        'user_auth_id': user_auth,
                        'form': VerifySMSForm,
                    }
                )

        else:
            return redirect('/login')    
    