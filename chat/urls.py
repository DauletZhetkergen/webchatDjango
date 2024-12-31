from django.urls import path
from . import views
from rest_framework_simplejwt import views as jwtView

urlpatterns = [
    path('', views.redirect_auth, name='empty'),
    path('login', views.login_page, name='login'),
    path('signup', views.signup_page, name='signup'),
    path('main', views.main_page, name='main')
]
