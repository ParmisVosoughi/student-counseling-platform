from django.urls import path
from .auth_views import LoginView, RefreshCookieView, LogoutView
urlpatterns=[path('login/',LoginView.as_view()),path('refresh/',RefreshCookieView.as_view()),path('logout/',LogoutView.as_view())]
