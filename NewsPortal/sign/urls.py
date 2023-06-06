"""
файл адресов для приложения "sign", которое отвечает за вход/регистрацию пользователей
"""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import upgrade_me, not_author

urlpatterns = [
    path('login/', LoginView.as_view(template_name='sign/login.html'),
         name='login'),
    path('logout/',
         LogoutView.as_view(template_name='sign/logout.html'),
         name='logout'),
    path('upgrade_me/', upgrade_me, name='author'),
    path('not_author/', not_author, name='not_author'),
]