from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.home, name="home"),
    path("pretest", views.pretest, name="pretest"),
    path("learning", views.learning, name="learning"),
    path("testing", views.testing, name="testing"),
    path("result/<int:test_score_id>/", views.result, name="result"),
]