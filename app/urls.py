from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("hot/", views.hot_questions, name="hot"),
    path("tag/<str:tag_name>/", views.tag_questions, name="tag"),
    path("question/<int:question_id>/", views.question_detail, name="question"),
    path("question/<int:question_id>/answer/", views.create_answer, name="create_answer"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("ask/", views.ask_question, name="ask"),
    path("settings/", views.SettingsView.as_view(), name="settings"),
    path("logout/", views.logout_view, name="logout")
]
