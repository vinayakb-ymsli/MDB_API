from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("test", views.test),
    path("create-client", views.create_client),
    path("create-project", views.create_project),
    path("create-model", views.create_model),
    path("contents", views.folder_contents),
]
