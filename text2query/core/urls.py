from django.urls import path
from .views import get_result, chat, clear_session, landing

urlpatterns = [
    path("", landing, name="landing"),
    path("chat", chat, name="chat"),
    path("home", get_result, name="home"),
    path("clear-session", clear_session, name="clear_session")
]
