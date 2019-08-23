from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf.urls import url
from django.contrib import admin
import django.contrib.auth.views

from . import views


urlpatterns = [
    url(r'^login/$', django.contrib.auth.views.LoginView.as_view()),
    url(r'^logout/$', django.contrib.auth.views.LogoutView.as_view()),

    url(r'^restricted/$', views.RestrictedView.as_view()),
    url(r'^trust/$', views.TrustView.as_view()),
    url(r'^session/$', views.SessionView.as_view()),
    url(r'^revoke/$', views.RevokeView.as_view()),
    url(r'^revoke_others/$', views.RevokeOthersView.as_view()),

    url(r'^admin/', admin.site.urls),
]
