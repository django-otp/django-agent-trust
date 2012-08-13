from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout'),

    url(r'^restricted/$', views.RestrictedView.as_view()),
    url(r'^trust/$', views.TrustView.as_view()),
    url(r'^session/$', views.SessionView.as_view()),
    url(r'^revoke/$', views.RevokeView.as_view()),
    url(r'^revoke_others/$', views.RevokeOthersView.as_view()),
)
