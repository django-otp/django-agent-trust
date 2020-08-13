from django.urls import path
from django.contrib import admin
import django.contrib.auth.views

from . import views


urlpatterns = [
    path('login/', django.contrib.auth.views.LoginView.as_view()),
    path('logout/', django.contrib.auth.views.LogoutView.as_view()),

    path('restricted/', views.RestrictedView.as_view()),
    path('trust/', views.TrustView.as_view()),
    path('session/', views.SessionView.as_view()),
    path('revoke/', views.RevokeView.as_view()),
    path('revoke_others/', views.RevokeOthersView.as_view()),

    path('admin/', admin.site.urls),
]
