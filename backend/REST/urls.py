from .views import *
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.urls import path

urlpatterns = [
    path('fetch', fetch, name='fetch'),
    path('', home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view()),
    path('fetch/listing', listing, name="listing"),
    path('profile', profile, name="profile"),
]