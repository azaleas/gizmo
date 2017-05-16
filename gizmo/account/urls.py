from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.dashboard, name = 'dashboard'),
    url(r'^login/$', views.LoginView.as_view(), name = 'login'),
    url(r'^verify-sms/$', views.VerifySMS.as_view(), name = 'verify'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name = 'logout'),
    url(r'^logout/$', auth_views.logout, name = 'logout'),
    url(r'^logout-then-login/$', auth_views.logout_then_login, 
        name = 'logout_then_login'),
    url(r'^password-change/$', auth_views.password_change, 
        {
            'post_change_redirect': 'account:password_change_done',
            'extra_context': {
                'section': 'change_password',
            },
        },
        name = 'password_change'),
    url(r'^password-change/done/$', auth_views.password_change_done, 
        name = 'password_change_done'),
    url(r'^password-reset/$', auth_views.password_reset, 
        {
            'post_reset_redirect': 'account:password_reset_done',
        },
        name = 'password_reset'),
    url(r'^password-reset/done/$', auth_views.password_reset_done, 
        name = 'password_reset_done'),
    url(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$', auth_views.password_reset_confirm, 
        {
            'post_reset_redirect': 'account:password_reset_complete',
        },
        name = 'password_reset_confirm'),
    url(r'^password-reset/complete/$', auth_views.password_reset_complete, 
        name = 'password_reset_complete'),
    url(r'^register/$', views.register, name = 'register'),
]