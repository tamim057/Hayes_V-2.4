from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login),
    path("on/", views.on_duty),
    path("off/", views.off_duty),
    path("bell/", views.bell),
    path("status/", views.status),
]