from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    
    path("home", views.home, name="home"),
    path("dashboard", views.dashboard, name="dashboard"),

    path("pretest", views.pretest, name="pretest"),

    path("learning/picsu", views.learning_picsu, name="learning-picsu"),
    path("learning/flashcard", views.learning_flashcard, name="learning-flashcard"),

    path("first_test/picsu", views.first_test_picsu, name="picsu-first-test"),
    path("first_test/flashcard", views.first_test_flashcard, name="flashcard-first-test"),
    
    path("retention_test/picsu", views.retention_test_picsu, name="picsu-retention-test"),
    path("retention_test/flashcard", views.retention_test_flashcard, name="flashcard-retention-test"),
    
    path("result/<int:test_score_id>/", views.result, name="result"),
]