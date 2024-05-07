from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.wiki, name="wiki"),
    path("search", views.search, name="search"),
    path("create-page", views.create_page, name="create-page"),
    path("edit-page/<str:title>", views.edit_page, name="edit-page"),
    path("random-page", views.random_page, name="random-page")
]
