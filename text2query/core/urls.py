from django.urls import path
from .views import home, api_query, landing

urlpatterns = [
    path("", landing, name="landing"),
    path("api/query/", api_query, name="api_query"),
    path("home/", home, name="home")
]
