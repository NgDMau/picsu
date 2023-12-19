from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("login", views.signin, name="login"),
    path('register', views.register, name='register'),
    path('logout', LogoutView.as_view(next_page='index'), name='logout'),
]